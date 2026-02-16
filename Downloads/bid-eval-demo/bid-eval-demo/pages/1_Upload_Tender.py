import streamlit as st
import json
from utils.state import (
    init_session_state,
    set_tender_data,
    get_tender_data,
    set_evaluation_criteria,
    get_evaluation_criteria,
)
from utils.pdf_parser import extract_text_from_file
from utils.ai_engine import extract_tender_data, generate_sample_tender_data
from utils.ui_helper import setup_sidebar

st.set_page_config(page_title="Upload Tender - Airo Bid Evaluation", page_icon="📄", layout="wide")

init_session_state()

# Set current page before sidebar setup
st.session_state.current_nav_page = "1_Upload_Tender"

selected_page = setup_sidebar()

# Handle page navigation
if selected_page == "2_Upload_Bids":
    st.switch_page("pages/2_Upload_Bids.py")
elif selected_page == "3_Dashboard":
    st.switch_page("pages/3_Dashboard.py")
elif selected_page == "4_Reports":
    st.switch_page("pages/4_Reports.py")
elif selected_page == "5_Chat":
    st.switch_page("pages/5_Chat.py")

# Page layout
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📄 Upload Tender Document")
with col2:
    st.markdown("### Step 1 of 5")

st.markdown("Upload your RFP/Tender document and extract evaluation criteria.")

# Tabs for upload and sample
tab1, tab2 = st.tabs(["Upload Document", "Use Sample Tender"])

with tab1:
    st.markdown("#### Upload Your Tender Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF, DOCX, or TXT file",
        type=["pdf", "docx", "txt"],
        help="Upload your RFP or tender document",
    )

    if uploaded_file is not None:
        with st.spinner("Analyzing tender document..."):
            try:
                # Extract text
                file_content = uploaded_file.read()
                file_extension = uploaded_file.name.split(".")[-1].lower()
                tender_text = extract_text_from_file(file_content, file_extension)

                # Send to Claude for analysis
                tender_data = extract_tender_data(tender_text)
                set_tender_data(tender_data)

                # Extract criteria
                criteria = tender_data.get("evaluation_criteria", [])
                set_evaluation_criteria(criteria)

                st.success("✓ Tender parsed successfully!")

                # Show summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Tender Title", tender_data.get("tender_title", "N/A")[:30] + "...")
                with col2:
                    st.metric("Organization", tender_data.get("issuing_organization", "N/A"))
                with col3:
                    st.metric("Criteria Count", len(criteria))

            except Exception as e:
                st.error(f"❌ Error processing tender: {str(e)}")
                st.info("Please ensure the file is a valid PDF, DOCX, or TXT document.")

with tab2:
    st.markdown("#### Load Sample Tender")
    st.markdown("Load a realistic sample tender for quick demonstration.")

    if st.button("Load Sample Tender", type="primary", use_container_width=True):
        with st.spinner("Loading sample tender..."):
            try:
                tender_data = generate_sample_tender_data()
                set_tender_data(tender_data)

                criteria = tender_data.get("evaluation_criteria", [])
                set_evaluation_criteria(criteria)

                st.success("✓ Sample tender loaded!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error loading sample: {str(e)}")

# Display current tender if loaded
if get_tender_data():
    st.markdown("---")
    tender_data = get_tender_data()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Tender Details")
        st.write(f"**Title:** {tender_data.get('tender_title', 'N/A')}")
        st.write(f"**Organization:** {tender_data.get('issuing_organization', 'N/A')}")
        st.write(f"**Reference:** {tender_data.get('tender_reference', 'N/A')}")
        st.write(f"**Deadline:** {tender_data.get('submission_deadline', 'N/A')}")
        st.write(f"**Duration:** {tender_data.get('contract_duration', 'N/A')}")

    with col2:
        st.markdown("### Scope of Work")
        st.write(tender_data.get("scope_of_work", "N/A"))

    # Evaluation Criteria Table
    st.markdown("---")
    st.markdown("### Evaluation Criteria")

    criteria = get_evaluation_criteria()

    if criteria:
        # Display criteria and allow weight adjustment
        st.markdown("Adjust evaluation criteria weights below if needed:")

        updated_criteria = []
        for i, criterion in enumerate(criteria):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"**{criterion.get('criterion', 'N/A')}**")

            with col2:
                category = criterion.get("category", "technical")
                st.caption(f"Category: {category}")

            with col3:
                weight = st.slider(
                    f"Weight {i}",
                    min_value=0,
                    max_value=100,
                    value=int(criterion.get("weight_percentage", 10)),
                    key=f"weight_{i}",
                    label_visibility="collapsed",
                )
                criterion["weight_percentage"] = weight
                updated_criteria.append(criterion)

        # Update session state with adjusted weights
        set_evaluation_criteria(updated_criteria)

        # Summary
        total_weight = sum(c.get("weight_percentage", 0) for c in updated_criteria)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Criteria", len(criteria))
        with col2:
            st.metric("Total Weight", f"{total_weight}%")
        with col3:
            if total_weight == 100:
                st.success("✓ Weights sum to 100%")
            else:
                st.warning(f"⚠️ Weights sum to {total_weight}% (target: 100%)")

        # Category breakdown
        st.markdown("---")
        st.markdown("### Category Breakdown")

        categories = {}
        for criterion in updated_criteria:
            cat = criterion.get("category", "technical")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(criterion.get("weight_percentage", 0))

        cols = st.columns(len(categories))
        for col, (cat, weights) in zip(cols, categories.items()):
            with col:
                st.metric(cat.title(), f"{sum(weights)}%", f"{len(weights)} criteria")

    # Show mandatory requirements
    st.markdown("---")
    st.markdown("### Mandatory Requirements")

    mandatory_reqs = tender_data.get("mandatory_requirements", [])
    if mandatory_reqs:
        for idx, req in enumerate(mandatory_reqs, 1):
            st.write(f"{idx}. {req}")
    else:
        st.info("No mandatory requirements specified")

    # Show technical specs
    st.markdown("---")
    st.markdown("### Key Technical Specifications")

    tech_specs = tender_data.get("technical_specifications", [])
    if tech_specs:
        for spec in tech_specs:
            st.write(f"• {spec}")
    else:
        st.info("No technical specifications provided")

    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.switch_page("pages/1_Upload_Tender.py")
    with col2:
        if st.button("Next: Upload Bids →", type="primary", use_container_width=True):
            st.switch_page("pages/2_Upload_Bids.py")

else:
    st.info("👆 Please upload a tender document or load the sample tender above to get started.")
