import streamlit as st
import json
from datetime import datetime
from utils.state import (
    init_session_state,
    get_tender_data,
    get_supplier_evaluations,
)
from utils.report_gen import BidEvaluationReportGenerator
from utils.ui_helper import setup_sidebar

st.set_page_config(page_title="Reports - Airo Bid Evaluation", page_icon="📑", layout="wide")

init_session_state()

# Set current page before sidebar setup
st.session_state.current_nav_page = "4_Reports"

selected_page = setup_sidebar()

# Handle page navigation
if selected_page == "1_Upload_Tender":
    st.switch_page("pages/1_Upload_Tender.py")
elif selected_page == "2_Upload_Bids":
    st.switch_page("pages/2_Upload_Bids.py")
elif selected_page == "3_Dashboard":
    st.switch_page("pages/3_Dashboard.py")
elif selected_page == "5_Chat":
    st.switch_page("pages/5_Chat.py")

# Load data
tender_data = get_tender_data()
evaluations = get_supplier_evaluations()

# Show info if not enough data
if not tender_data or len(evaluations) < 2:
    st.info("ℹ️ Upload a tender and evaluate bids on Pages 1-2 to generate reports.")

# Page layout
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📑 Download Reports")
with col2:
    st.markdown("### Step 4 of 5")

st.markdown(f"**Tender:** {tender_data.get('tender_title', 'N/A')}")
st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Report Generator
report_gen = BidEvaluationReportGenerator()

# Sort evaluations by score
sorted_evals = sorted(evaluations, key=lambda x: float(x.get("overall_score", 0)), reverse=True)

# Report generation options
st.markdown("---")
st.markdown("### Available Reports")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📄 Executive Summary")
    st.markdown(
        """
        One-page summary with:
        - Tender details
        - Supplier ranking
        - Top recommendation
        - Key risks
        """
    )

    if st.button("Generate Executive Summary", key="exec_summary", use_container_width=True):
        with st.spinner("Generating Executive Summary..."):
            try:
                pdf_content = report_gen.generate_executive_summary(tender_data, sorted_evals)

                st.download_button(
                    label="📥 Download Executive Summary PDF",
                    data=pdf_content,
                    file_name=f"Executive_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_exec",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")

with col2:
    st.markdown("#### 📊 Comparative Analysis")
    st.markdown(
        """
        Multi-page report with:
        - Score comparison matrix
        - Compliance matrix
        - Trade-off analysis
        - Detailed comparisons
        """
    )

    if st.button("Generate Comparative Analysis", key="comp_analysis", use_container_width=True):
        with st.spinner("Generating Comparative Analysis..."):
            try:
                trade_off = getattr(st.session_state, "trade_off_analysis", "")
                pdf_content = report_gen.generate_comparative_report(
                    tender_data, sorted_evals, trade_off
                )

                st.download_button(
                    label="📥 Download Comparative Analysis PDF",
                    data=pdf_content,
                    file_name=f"Comparative_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_comp",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")

# Individual Supplier Reports
st.markdown("---")
st.markdown("### Individual Supplier Reports")

st.markdown("Generate detailed reports for specific suppliers:")

for eval_data in sorted_evals:
    supplier_name = eval_data.get("supplier_name", "Unknown")

    with st.expander(f"📋 {supplier_name}", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{supplier_name}**")
            st.write(f"Score: {float(eval_data.get('overall_score', 0)):.0f}/100")
            st.write(f"Country: {eval_data.get('supplier_country', 'N/A')}")
            st.write(f"Price: {eval_data.get('proposed_price', 'N/A')}")

        with col2:
            if st.button(f"📥 Download Report", key=f"supplier_{supplier_name}", use_container_width=True):
                with st.spinner(f"Generating report for {supplier_name}..."):
                    try:
                        # For now, generate a comparative report filtered to this supplier
                        pdf_content = report_gen.generate_comparative_report(
                            tender_data, [eval_data], ""
                        )

                        st.download_button(
                            label=f"📥 {supplier_name} Report",
                            data=pdf_content,
                            file_name=f"{supplier_name}_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            key=f"download_{supplier_name}",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Data Export
st.markdown("---")
st.markdown("### Data Export")

col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Export Evaluation Data (JSON)", use_container_width=True):
        export_data = {
            "tender": tender_data,
            "evaluations": evaluations,
            "generated_at": datetime.now().isoformat(),
        }

        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"bid_evaluation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key="download_json",
            use_container_width=True,
        )

with col2:
    if st.button("📥 Export Rankings (CSV)", use_container_width=True):
        import pandas as pd

        ranking_data = []
        for idx, eval_data in enumerate(sorted_evals, 1):
            ranking_data.append(
                {
                    "Rank": idx,
                    "Supplier": eval_data.get("supplier_name", "N/A"),
                    "Country": eval_data.get("supplier_country", "N/A"),
                    "Overall Score": float(eval_data.get("overall_score", 0)),
                    "Technical": float(eval_data.get("category_scores", {}).get("technical", {}).get("score", 0)),
                    "Commercial": float(eval_data.get("category_scores", {}).get("commercial", {}).get("score", 0)),
                    "Compliance": float(eval_data.get("category_scores", {}).get("compliance", {}).get("score", 0)),
                    "Price": eval_data.get("proposed_price", "N/A"),
                    "Timeline": eval_data.get("proposed_timeline", "N/A"),
                }
            )

        ranking_df = pd.DataFrame(ranking_data)
        csv = ranking_df.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"bid_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_csv",
            use_container_width=True,
        )

# Report Templates Info
with st.expander("ℹ️ About These Reports"):
    st.markdown(
        """
        ### Report Details

        **Executive Summary**
        - Professional one-page overview
        - Top recommendation with reasoning
        - Key supplier rankings
        - Risk highlights
        - Airo branding and confidentiality marking

        **Comparative Analysis**
        - Multi-supplier comparison
        - Score comparison charts
        - Compliance matrix
        - Trade-off analysis narrative
        - Detailed evidence and recommendations

        **Individual Supplier Reports**
        - Detailed evaluation for specific supplier
        - Score breakdown by category
        - Criterion-level scoring with evidence
        - Strengths, gaps, and risks
        - HSE/ESG compliance status

        All reports include:
        - Professional Airo branding
        - Date and tender reference
        - "Confidential" watermark
        - Page numbers
        - Source traceability note
        - Evaluator sign-off section
        """
    )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("← Back", use_container_width=True):
        st.switch_page("pages/3_Dashboard.py")
with col2:
    st.empty()
with col3:
    if st.button("Next: Chat →", type="primary", use_container_width=True):
        st.switch_page("pages/5_Chat.py")
