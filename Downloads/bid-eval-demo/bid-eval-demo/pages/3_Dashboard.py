import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.state import (
    init_session_state,
    get_tender_data,
    get_supplier_evaluations,
    get_evaluation_criteria,
)
from utils.ai_engine import generate_trade_off_analysis
from utils.ui_helper import setup_sidebar

st.set_page_config(page_title="Dashboard - Airo Bid Evaluation", page_icon="📊", layout="wide")

init_session_state()

# Set current page before sidebar setup
st.session_state.current_nav_page = "3_Dashboard"

selected_page = setup_sidebar()

# Handle page navigation
if selected_page == "1_Upload_Tender":
    st.switch_page("pages/1_Upload_Tender.py")
elif selected_page == "2_Upload_Bids":
    st.switch_page("pages/2_Upload_Bids.py")
elif selected_page == "4_Reports":
    st.switch_page("pages/4_Reports.py")
elif selected_page == "5_Chat":
    st.switch_page("pages/5_Chat.py")

# Load data
tender_data = get_tender_data()
evaluations = get_supplier_evaluations()

# Show info if not enough data
if not tender_data or len(evaluations) < 2:
    st.info("ℹ️ Upload a tender and at least 2 bids on Pages 1-2 to view the dashboard.")

# Page layout
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 Bid Evaluation Dashboard")
with col2:
    st.markdown("### Step 3 of 5")

st.markdown(f"**Tender:** {tender_data.get('tender_title', 'N/A')}")

# Sort evaluations by overall score
sorted_evals = sorted(evaluations, key=lambda x: float(x.get("overall_score", 0)), reverse=True)

# Tab 1: Overall Ranking
with st.container():
    st.markdown("---")
    st.markdown("### 1️⃣ Overall Ranking")

    # Create ranking table
    ranking_data = []
    for idx, eval_data in enumerate(sorted_evals, 1):
        ranking_data.append(
            {
                "Rank": idx,
                "Supplier": eval_data.get("supplier_name", "N/A"),
                "Overall": float(eval_data.get("overall_score", 0)),
                "Technical": float(eval_data.get("category_scores", {}).get("technical", {}).get("score", 0)),
                "Commercial": float(eval_data.get("category_scores", {}).get("commercial", {}).get("score", 0)),
                "Compliance": float(eval_data.get("category_scores", {}).get("compliance", {}).get("score", 0)),
                "Completeness": eval_data.get("completeness_percentage", 0),
                "Recommendation": "✓ Recommended"
                if float(eval_data.get("overall_score", 0)) >= 80
                else "◐ Conditional"
                if float(eval_data.get("overall_score", 0)) >= 70
                else "✗ Not Recommended",
            }
        )

    ranking_df = pd.DataFrame(ranking_data)

    # Style the dataframe
    def color_recommendation(val):
        if "Recommended" in str(val) and "Not" not in str(val):
            return "background-color: #d4f4dd"
        elif "Conditional" in str(val):
            return "background-color: #fff3cd"
        else:
            return "background-color: #f8d7da"

    styled_df = ranking_df.style.applymap(color_recommendation, subset=["Recommendation"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Tab 2: Score Comparison Charts
with st.container():
    st.markdown("---")
    st.markdown("### 2️⃣ Score Comparison Charts")

    col1, col2 = st.columns(2)

    with col1:
        # Spider/Radar chart
        suppliers = [e.get("supplier_name", "N/A") for e in sorted_evals]
        technical_scores = [float(e.get("category_scores", {}).get("technical", {}).get("score", 0)) for e in sorted_evals]
        commercial_scores = [float(e.get("category_scores", {}).get("commercial", {}).get("score", 0)) for e in sorted_evals]
        compliance_scores = [float(e.get("category_scores", {}).get("compliance", {}).get("score", 0)) for e in sorted_evals]

        fig = go.Figure()

        for i, supplier in enumerate(suppliers):
            fig.add_trace(
                go.Scatterpolar(
                    r=[technical_scores[i], commercial_scores[i], compliance_scores[i]],
                    theta=["Technical", "Commercial", "Compliance"],
                    fill="toself",
                    name=supplier,
                )
            )

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=400,
            title="Score Comparison by Category",
            hovermode="closest",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Completeness chart
        completeness_data = [e.get("completeness_percentage", 0) for e in sorted_evals]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=suppliers,
                    y=completeness_data,
                    marker_color="#E63028",
                    text=[f"{int(c)}%" for c in completeness_data],
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            title="Bid Completeness %",
            xaxis_title="Supplier",
            yaxis_title="Completeness %",
            height=400,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    # Grouped bar chart for all scores
    st.markdown("#### Score Breakdown by Supplier")

    fig = go.Figure(
        data=[
            go.Bar(name="Technical", x=suppliers, y=technical_scores, marker_color="#1f77b4"),
            go.Bar(name="Commercial", x=suppliers, y=commercial_scores, marker_color="#ff7f0e"),
            go.Bar(name="Compliance", x=suppliers, y=compliance_scores, marker_color="#2ca02c"),
        ]
    )

    fig.update_layout(
        barmode="group",
        title="Scores by Category and Supplier",
        xaxis_title="Supplier",
        yaxis_title="Score",
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)

# Tab 3: Compliance Matrix
with st.container():
    st.markdown("---")
    st.markdown("### 3️⃣ Compliance Matrix")

    # Get all mandatory requirements
    all_requirements = set()
    for eval_data in sorted_evals:
        for req in eval_data.get("mandatory_requirements_status", []):
            all_requirements.add(req.get("requirement", ""))

    # Build compliance matrix
    compliance_matrix_data = []
    for req in sorted(all_requirements):
        row = {"Requirement": req}
        for eval_data in sorted_evals:
            status = "?"
            for req_status in eval_data.get("mandatory_requirements_status", []):
                if req_status.get("requirement") == req:
                    status_val = req_status.get("status", "unclear")
                    status = "✓" if status_val == "compliant" else "✗" if status_val == "non_compliant" else "◐"
                    break
            row[eval_data.get("supplier_name", "N/A")] = status
        compliance_matrix_data.append(row)

    compliance_df = pd.DataFrame(compliance_matrix_data)

    # Color the status columns
    def color_compliance(val):
        if val == "✓":
            return "background-color: #d4f4dd; color: #155724; font-weight: bold;"
        elif val == "✗":
            return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
        elif val == "◐":
            return "background-color: #fff3cd; color: #856404; font-weight: bold;"
        return ""

    styled_compliance_df = compliance_df.style.applymap(color_compliance, subset=[col for col in compliance_df.columns if col != "Requirement"])
    st.dataframe(styled_compliance_df, use_container_width=True, hide_index=True)

    # HSE and ESG Status
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### HSE & ESG Compliance")
        for eval_data in sorted_evals:
            supplier = eval_data.get("supplier_name", "N/A")
            hse_status = eval_data.get("hse_compliance", {}).get("status", "unclear")
            esg_status = eval_data.get("esg_compliance", {}).get("status", "unclear")

            col1a, col1b, col1c = st.columns([2, 1, 1])
            with col1a:
                st.write(f"**{supplier}**")
            with col1b:
                hse_icon = "✓" if hse_status == "compliant" else "✗" if hse_status == "non_compliant" else "◐"
                st.write(f"HSE: {hse_icon}")
            with col1c:
                esg_icon = "✓" if esg_status == "compliant" else "✗" if esg_status == "non_compliant" else "◐"
                st.write(f"ESG: {esg_icon}")

    with col2:
        st.markdown("#### ISO Certifications")
        for eval_data in sorted_evals:
            supplier = eval_data.get("supplier_name", "N/A")
            certifications = eval_data.get("iso_certifications", [])
            with st.expander(supplier):
                if certifications:
                    for cert in certifications:
                        st.write(f"• {cert}")
                else:
                    st.write("No certifications listed")

# Tab 4: Risk Heatmap
with st.container():
    st.markdown("---")
    st.markdown("### 4️⃣ Key Risks by Supplier")

    for eval_data in sorted_evals:
        supplier = eval_data.get("supplier_name", "N/A")
        risks = eval_data.get("key_risks", [])

        col1, col2 = st.columns([2, 3])
        with col1:
            overall_score = float(eval_data.get("overall_score", 0))
            st.metric(supplier, f"{overall_score:.0f}/100")

        with col2:
            if risks:
                for risk in risks:
                    st.write(f"⚠️ {risk}")
            else:
                st.write("No significant risks identified")

# Tab 5: Recommendation Summary
with st.container():
    st.markdown("---")
    st.markdown("### 5️⃣ Recommendation Summary")

    top_supplier = sorted_evals[0]
    top_name = top_supplier.get("supplier_name", "N/A")
    top_score = float(top_supplier.get("overall_score", 0))

    col1, col2 = st.columns([2, 1])

    with col1:
        st.success(f"### ✓ Recommended Vendor: {top_name}")
        st.markdown(f"**Overall Score:** {top_score:.0f}/100")

        st.markdown("**Key Strengths:**")
        strengths = top_supplier.get("category_scores", {}).get("technical", {}).get("strengths", [])
        for strength in strengths:
            st.write(f"• {strength}")

    with col2:
        st.markdown("**Gaps:**")
        gaps = top_supplier.get("category_scores", {}).get("technical", {}).get("gaps", [])
        if gaps:
            for gap in gaps:
                st.write(f"• {gap}")
        else:
            st.write("No significant gaps")

    # Trade-off Analysis
    st.markdown("---")
    st.markdown("### 6️⃣ Trade-off Analysis")

    if st.button("Generate Trade-off Analysis", type="secondary", use_container_width=True):
        with st.spinner("Generating trade-off analysis..."):
            try:
                evaluation_summary = {
                    "tender_title": tender_data.get("tender_title", ""),
                    "suppliers": [
                        {
                            "name": e.get("supplier_name"),
                            "score": float(e.get("overall_score", 0)),
                            "technical": float(e.get("category_scores", {}).get("technical", {}).get("score", 0)),
                            "commercial": float(e.get("category_scores", {}).get("commercial", {}).get("score", 0)),
                            "compliance": float(e.get("category_scores", {}).get("compliance", {}).get("score", 0)),
                            "strengths": e.get("category_scores", {}).get("technical", {}).get("strengths", []),
                            "gaps": e.get("category_scores", {}).get("technical", {}).get("gaps", []),
                            "price": e.get("proposed_price", "N/A"),
                        }
                        for e in sorted_evals[:3]
                    ],
                }

                trade_off_text = generate_trade_off_analysis(
                    tender_data.get("tender_title", ""), evaluation_summary
                )

                st.markdown(trade_off_text)

                # Store in session for reports
                st.session_state.trade_off_analysis = trade_off_text

            except Exception as e:
                st.error(f"❌ Error generating analysis: {str(e)}")
    elif "trade_off_analysis" in st.session_state:
        st.markdown(st.session_state.trade_off_analysis)

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("← Back", use_container_width=True):
        st.switch_page("pages/2_Upload_Bids.py")
with col2:
    st.empty()
with col3:
    if st.button("Next: Reports →", type="primary", use_container_width=True):
        st.switch_page("pages/4_Reports.py")
