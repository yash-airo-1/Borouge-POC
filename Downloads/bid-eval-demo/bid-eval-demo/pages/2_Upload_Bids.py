import streamlit as st
import json
from utils.state import (
    init_session_state,
    get_tender_data,
    get_evaluation_criteria,
    get_supplier_evaluations,
    set_supplier_evaluations,
)
from utils.pdf_parser import extract_text_from_file
from utils.ai_engine import evaluate_supplier_bid, generate_sample_supplier_evaluations
from utils.ui_helper import setup_sidebar

st.set_page_config(page_title="Upload Bids - Airo Bid Evaluation", page_icon="📋", layout="wide")

init_session_state()

# Set current page before sidebar setup
st.session_state.current_nav_page = "2_Upload_Bids"

selected_page = setup_sidebar()

# Handle page navigation
if selected_page == "1_Upload_Tender":
    st.switch_page("pages/1_Upload_Tender.py")
elif selected_page == "3_Dashboard":
    st.switch_page("pages/3_Dashboard.py")
elif selected_page == "4_Reports":
    st.switch_page("pages/4_Reports.py")
elif selected_page == "5_Chat":
    st.switch_page("pages/5_Chat.py")

# Check if tender is loaded (but allow access anyway)
if not get_tender_data():
    st.info("ℹ️ Tip: Upload a tender document first on Page 1 for best results.")

# Page layout
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📋 Upload Supplier Responses")
with col2:
    st.markdown("### Step 2 of 5")

st.markdown("Upload supplier bid responses for evaluation against the tender criteria.")

# Tabs for upload and sample
tab1, tab2 = st.tabs(["Upload Bids", "Load Sample Bids"])

with tab1:
    st.markdown("#### Upload Supplier Bid Responses")

    uploaded_files = st.file_uploader(
        "Choose PDF, DOCX, or TXT files (max 10 files)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Each file should be one supplier's bid response",
    )

    if uploaded_files:
        if len(uploaded_files) > 10:
            st.error("❌ Maximum 10 files allowed. Please upload fewer files.")
        else:
            if st.button("Evaluate All Bids", type="primary", use_container_width=True):
                with st.spinner("Evaluating bids..."):
                    tender_data = get_tender_data()
                    criteria = get_evaluation_criteria()

                    # Create progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    evaluations = []
                    errors = []

                    for idx, uploaded_file in enumerate(uploaded_files, 1):
                        try:
                            status_text.text(f"Evaluating {idx}/{len(uploaded_files)}: {uploaded_file.name}")
                            progress = idx / len(uploaded_files)
                            progress_bar.progress(progress)

                            # Extract text
                            file_content = uploaded_file.read()
                            file_extension = uploaded_file.name.split(".")[-1].lower()
                            bid_text = extract_text_from_file(file_content, file_extension)

                            # Evaluate with Claude
                            evaluation = evaluate_supplier_bid(bid_text, tender_data, criteria)
                            evaluations.append(evaluation)

                        except Exception as e:
                            errors.append(f"{uploaded_file.name}: {str(e)}")

                    # Save evaluations
                    set_supplier_evaluations(evaluations)

                    progress_bar.empty()
                    status_text.empty()

                    if evaluations:
                        st.success(f"✓ Successfully evaluated {len(evaluations)} bid(s)!")

                    if errors:
                        with st.expander("⚠️ Errors during evaluation"):
                            for error in errors:
                                st.write(f"• {error}")

with tab2:
    st.markdown("#### Load Sample Bids")
    st.markdown("Load realistic sample bids for quick demonstration.")

    if st.button("Load Sample Bids", type="primary", use_container_width=True):
        with st.spinner("Loading sample bids..."):
            try:
                sample_evaluations = generate_sample_supplier_evaluations()
                set_supplier_evaluations(sample_evaluations)
                st.success(f"✓ Loaded {len(sample_evaluations)} sample bids!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading samples: {str(e)}")

# Display current bids
st.markdown("---")

evaluations = get_supplier_evaluations()

if evaluations:
    st.markdown("### Evaluated Bids Summary")
    st.metric("Total Bids Evaluated", len(evaluations))

    # Sort by score
    sorted_evals = sorted(evaluations, key=lambda x: float(x.get("overall_score", 0)), reverse=True)

    # Display cards for each supplier
    for i, evaluation in enumerate(sorted_evals):
        col1, col2, col3, col4 = st.columns(4)

        supplier_name = evaluation.get("supplier_name", "Unknown")
        overall_score = float(evaluation.get("overall_score", 0))
        completeness = evaluation.get("completeness_percentage", 0)

        with col1:
            st.metric(supplier_name, f"{overall_score:.0f}/100")

        with col2:
            tech = float(evaluation.get("category_scores", {}).get("technical", {}).get("score", 0))
            st.metric("Technical", f"{tech:.0f}")

        with col3:
            comm = float(evaluation.get("category_scores", {}).get("commercial", {}).get("score", 0))
            st.metric("Commercial", f"{comm:.0f}")

        with col4:
            comp = float(evaluation.get("category_scores", {}).get("compliance", {}).get("score", 0))
            st.metric("Compliance", f"{comp:.0f}")

        with st.expander(f"📋 {supplier_name} - Details"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Supplier Info**")
                st.write(f"Country: {evaluation.get('supplier_country', 'N/A')}")
                st.write(f"Reference: {evaluation.get('bid_reference', 'N/A')}")
                st.write(f"Price: {evaluation.get('proposed_price', 'N/A')}")
                st.write(f"Timeline: {evaluation.get('proposed_timeline', 'N/A')}")
                st.write(f"Completeness: {completeness}%")

            with col2:
                st.markdown("**Strengths**")
                strengths = evaluation.get("category_scores", {}).get("technical", {}).get("strengths", [])
                for strength in strengths[:3]:
                    st.write(f"✓ {strength}")

            st.markdown("**Key Gaps**")
            gaps = evaluation.get("category_scores", {}).get("technical", {}).get("gaps", [])
            for gap in gaps[:3]:
                st.write(f"✗ {gap}")

            st.markdown("**Key Risks**")
            risks = evaluation.get("key_risks", [])
            for risk in risks[:3]:
                st.write(f"⚠️ {risk}")

            st.markdown("**Recommendation**")
            st.write(evaluation.get("recommendation", "N/A"))

else:
    st.info("👆 Upload supplier bids above or load sample bids to get started.")

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("← Back", use_container_width=True):
        st.switch_page("pages/1_Upload_Tender.py")
with col2:
    st.empty()
with col3:
    if len(evaluations) >= 2:
        if st.button("Next: Dashboard →", type="primary", use_container_width=True):
            st.switch_page("pages/3_Dashboard.py")
    else:
        st.button("Next: Dashboard →", type="primary", use_container_width=True, disabled=True)
        st.caption("⚠️ Evaluate at least 2 bids to view dashboard")
