from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
from typing import Dict, List, Any


class BidEvaluationReportGenerator:
    """Generate professional PDF reports for bid evaluation."""

    def __init__(self):
        self.airo_red = colors.HexColor("#E63028")
        self.airo_black = colors.HexColor("#1A1A1A")
        self.airo_white = colors.HexColor("#FFFFFF")
        self.light_grey = colors.HexColor("#F5F5F5")
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=self.airo_red,
                spaceAfter=12,
                alignment=TA_CENTER,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CustomHeading",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=self.airo_black,
                spaceAfter=10,
                spaceBefore=10,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CustomBody",
                parent=self.styles["BodyText"],
                fontSize=10,
                alignment=TA_LEFT,
            )
        )

    def create_header(self):
        """Create header with Airo branding."""
        data = [
            [
                Paragraph(
                    "<b>AIRO DIGITAL LABS</b>",
                    ParagraphStyle(
                        "header", parent=self.styles["Normal"], fontSize=14, textColor=self.airo_red
                    ),
                ),
                Paragraph(
                    f"<b>Date: {datetime.now().strftime('%Y-%m-%d')}</b>",
                    ParagraphStyle(
                        "headerright", parent=self.styles["Normal"], fontSize=10, alignment=TA_RIGHT
                    ),
                ),
            ]
        ]
        t = Table(data, colWidths=[3.5 * inch, 2.5 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), self.airo_white),
                    ("TEXTCOLOR", (0, 0), (-1, -1), self.airo_black),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("LINEBELOW", (0, 0), (-1, -1), 2, self.airo_red),
                ]
            )
        )
        return t

    def score_to_color(self, score: float) -> colors.Color:
        """Convert a score to a color (green=high, yellow=medium, red=low)."""
        score = float(score)
        if score >= 85:
            return colors.HexColor("#27AE60")  # Green
        elif score >= 70:
            return colors.HexColor("#F39C12")  # Orange
        else:
            return colors.HexColor("#E74C3C")  # Red

    def generate_executive_summary(
        self, tender_data: Dict[str, Any], supplier_evaluations: List[Dict[str, Any]]
    ) -> bytes:
        """Generate executive summary PDF report."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

        story = []

        # Header
        story.append(self.create_header())
        story.append(Spacer(1, 0.3 * inch))

        # Title
        story.append(
            Paragraph(
                "EXECUTIVE SUMMARY",
                self.styles["CustomTitle"],
            )
        )
        story.append(Spacer(1, 0.2 * inch))

        # Tender Info
        tender_info_data = [
            ["Tender Title:", tender_data.get("tender_title", "N/A")],
            ["Tender Reference:", tender_data.get("tender_reference", "N/A")],
            ["Organization:", tender_data.get("issuing_organization", "N/A")],
            ["Date Generated:", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Number of Bidders:", str(len(supplier_evaluations))],
        ]
        tender_table = Table(tender_info_data, colWidths=[2 * inch, 4 * inch])
        tender_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [self.light_grey, self.airo_white]),
                ]
            )
        )
        story.append(tender_table)
        story.append(Spacer(1, 0.3 * inch))

        # Ranking Table
        story.append(Paragraph("SUPPLIER RANKING", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1 * inch))

        # Sort suppliers by overall score
        sorted_suppliers = sorted(supplier_evaluations, key=lambda x: float(x.get("overall_score", 0)), reverse=True)

        ranking_data = [["Rank", "Supplier", "Score", "Technical", "Commercial", "Compliance", "Recommendation"]]
        for idx, supplier in enumerate(sorted_suppliers[:5], 1):
            score = float(supplier.get("overall_score", 0))
            tech_score = float(supplier.get("category_scores", {}).get("technical", {}).get("score", 0))
            comm_score = float(supplier.get("category_scores", {}).get("commercial", {}).get("score", 0))
            comp_score = float(supplier.get("category_scores", {}).get("compliance", {}).get("score", 0))

            ranking_data.append(
                [
                    str(idx),
                    supplier.get("supplier_name", "N/A"),
                    f"{score:.0f}",
                    f"{tech_score:.0f}",
                    f"{comm_score:.0f}",
                    f"{comp_score:.0f}",
                    "✓" if score >= 80 else "◐" if score >= 70 else "✗",
                ]
            )

        ranking_table = Table(ranking_data, colWidths=[0.6 * inch, 2 * inch, 0.8 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch])
        ranking_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), self.airo_red),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("TOPPADDING", (0, 0), (-1, 0), 12),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, self.light_grey]),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ]
            )
        )
        story.append(ranking_table)
        story.append(Spacer(1, 0.3 * inch))

        # Recommendation
        if sorted_suppliers:
            top_supplier = sorted_suppliers[0]
            story.append(Paragraph("TOP RECOMMENDATION", self.styles["CustomHeading"]))
            story.append(Spacer(1, 0.1 * inch))

            rec_text = f"""
            <b>{top_supplier.get('supplier_name', 'N/A')}</b> is recommended as the preferred vendor.
            <br/><br/>
            Overall Score: <b>{float(top_supplier.get('overall_score', 0)):.0f}/100</b>
            <br/><br/>
            Key Strengths:<br/>
            {self._format_list(top_supplier.get('category_scores', {}).get('technical', {}).get('strengths', []))}
            """
            story.append(Paragraph(rec_text, self.styles["CustomBody"]))

        story.append(Spacer(1, 0.3 * inch))

        # Risk Summary
        story.append(Paragraph("KEY RISKS IDENTIFIED", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1 * inch))

        risk_text = ""
        for supplier in sorted_suppliers[:3]:
            risks = supplier.get("key_risks", [])
            if risks:
                risk_text += f"<b>{supplier.get('supplier_name')}:</b> {', '.join(risks)}<br/><br/>"

        if risk_text:
            story.append(Paragraph(risk_text, self.styles["CustomBody"]))

        # Footer
        story.append(Spacer(1, 0.5 * inch))
        story.append(
            Paragraph(
                "<i>This evaluation was generated using Airo's AI-Powered Bid Evaluation Platform. All scores are based on analysis of submitted bid documents.</i>",
                ParagraphStyle("footer", parent=self.styles["Normal"], fontSize=8, textColor=colors.grey),
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_comparative_report(
        self,
        tender_data: Dict[str, Any],
        supplier_evaluations: List[Dict[str, Any]],
        trade_off_analysis: str,
    ) -> bytes:
        """Generate comparative analysis PDF report."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

        story = []

        # Header
        story.append(self.create_header())
        story.append(Spacer(1, 0.3 * inch))

        # Title
        story.append(
            Paragraph(
                "COMPARATIVE ANALYSIS",
                self.styles["CustomTitle"],
            )
        )
        story.append(Spacer(1, 0.2 * inch))

        # Comparative Table
        story.append(Paragraph("SCORE COMPARISON MATRIX", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1 * inch))

        sorted_suppliers = sorted(supplier_evaluations, key=lambda x: float(x.get("overall_score", 0)), reverse=True)

        comp_data = [["Supplier", "Overall", "Technical", "Commercial", "Compliance", "Completeness"]]
        for supplier in sorted_suppliers:
            comp_data.append(
                [
                    supplier.get("supplier_name", "N/A"),
                    f"{float(supplier.get('overall_score', 0)):.0f}",
                    f"{float(supplier.get('category_scores', {}).get('technical', {}).get('score', 0)):.0f}",
                    f"{float(supplier.get('category_scores', {}).get('commercial', {}).get('score', 0)):.0f}",
                    f"{float(supplier.get('category_scores', {}).get('compliance', {}).get('score', 0)):.0f}",
                    f"{supplier.get('completeness_percentage', 0)}%",
                ]
            )

        comp_table = Table(comp_data, colWidths=[2 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch])
        comp_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), self.airo_red),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, self.light_grey]),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ]
            )
        )
        story.append(comp_table)
        story.append(Spacer(1, 0.3 * inch))

        # Compliance Matrix
        story.append(Paragraph("MANDATORY REQUIREMENTS COMPLIANCE", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1 * inch))

        # Get unique mandatory requirements
        all_requirements = set()
        for supplier in supplier_evaluations:
            for req in supplier.get("mandatory_requirements_status", []):
                all_requirements.add(req.get("requirement", ""))

        comp_matrix_data = [["Requirement"] + [s.get("supplier_name", "N/A") for s in sorted_suppliers]]

        for req in sorted(all_requirements):
            row = [req]
            for supplier in sorted_suppliers:
                status = "?"
                for req_status in supplier.get("mandatory_requirements_status", []):
                    if req_status.get("requirement") == req:
                        stat = req_status.get("status", "unclear")
                        status = "✓" if stat == "compliant" else "✗" if stat == "non_compliant" else "◐"
                        break
                row.append(status)
            comp_matrix_data.append(row)

        comp_matrix = Table(comp_matrix_data, colWidths=[2.5 * inch] + [1 * inch] * len(sorted_suppliers))
        comp_matrix.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), self.airo_red),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, self.light_grey]),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ]
            )
        )
        story.append(comp_matrix)
        story.append(Spacer(1, 0.3 * inch))

        # Trade-off Analysis
        story.append(Paragraph("TRADE-OFF ANALYSIS", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1 * inch))

        if trade_off_analysis:
            story.append(Paragraph(trade_off_analysis, self.styles["CustomBody"]))

        # Footer
        story.append(Spacer(1, 0.5 * inch))
        story.append(
            Paragraph(
                "<i>This evaluation was generated using Airo's AI-Powered Bid Evaluation Platform. All scores are based on analysis of submitted bid documents.</i>",
                ParagraphStyle("footer", parent=self.styles["Normal"], fontSize=8, textColor=colors.grey),
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _format_list(self, items: List[str]) -> str:
        """Format a list as HTML bullet points."""
        if not items:
            return ""
        return "• " + "<br/>• ".join(items)
