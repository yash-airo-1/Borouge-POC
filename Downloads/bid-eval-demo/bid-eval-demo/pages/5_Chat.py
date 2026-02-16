import streamlit as st
import json
from utils.state import (
    init_session_state,
    get_tender_data,
    get_supplier_evaluations,
    get_evaluation_criteria,
    get_chat_history,
    add_chat_message,
)
from utils.ai_engine import chat_with_evaluation_data
from utils.ui_helper import setup_sidebar

st.set_page_config(page_title="Chat - Airo Bid Evaluation", page_icon="💬", layout="wide")

init_session_state()

# Set current page before sidebar setup
st.session_state.current_nav_page = "5_Chat"

selected_page = setup_sidebar()

# Handle page navigation
if selected_page == "1_Upload_Tender":
    st.switch_page("pages/1_Upload_Tender.py")
elif selected_page == "2_Upload_Bids":
    st.switch_page("pages/2_Upload_Bids.py")
elif selected_page == "3_Dashboard":
    st.switch_page("pages/3_Dashboard.py")
elif selected_page == "4_Reports":
    st.switch_page("pages/4_Reports.py")

# Load data
tender_data = get_tender_data()
evaluations = get_supplier_evaluations()
criteria = get_evaluation_criteria()

# Show info if not enough data
if not tender_data or len(evaluations) < 2:
    st.info("ℹ️ Upload a tender and evaluate bids on Pages 1-2 to use the chat assistant.")

# Page layout
col1, col2 = st.columns([3, 1])
with col1:
    st.title("💬 Bid Intelligence Assistant")
with col2:
    st.markdown("### Step 5 of 5")

st.markdown("Ask questions about the bids, suppliers, scores, and recommendations.")

# Sidebar with quick actions
with st.sidebar:
    st.markdown("### Quick Actions")
    quick_actions = [
        "Compare top 2 suppliers",
        "Show compliance gaps",
        "ESG status all bidders",
        "Risk summary",
        "Management summary",
    ]

    for action in quick_actions:
        if st.button(f"📌 {action}", use_container_width=True, key=f"quick_{action}"):
            st.session_state.user_input = action
            st.rerun()

    st.markdown("---")
    st.markdown("### Tips")
    st.markdown(
        """
        Try asking:
        - "Which supplier has the best ESG score?"
        - "What are the risks with the cheapest bid?"
        - "Compare warranty terms"
        - "Is Supplier X HSE compliant?"
        - "Show compliance matrix"
        - "Summarize for management"
        """
    )

# Chat interface
st.markdown("---")

# Display chat history
chat_history = get_chat_history()

for message in chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# User input
user_input = st.chat_input("Ask a question about the bids...", key="chat_input")

# Handle quick action button input
if "user_input" in st.session_state and st.session_state.user_input:
    user_input = st.session_state.user_input
    st.session_state.user_input = None

if user_input:
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Add to chat history
    add_chat_message("user", user_input)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = chat_with_evaluation_data(
                    user_input,
                    tender_data,
                    evaluations,
                    criteria,
                    get_chat_history()[:-1],  # Exclude the last user message we just added
                )

                st.markdown(response)

                # Add response to chat history
                add_chat_message("assistant", response)

                # Check if user asked to update weights
                if "weight" in user_input.lower() or "criteria" in user_input.lower():
                    st.info("💡 Switch to the Dashboard tab to see updated rankings if criteria weights were changed.")

            except Exception as e:
                st.error(f"❌ Error getting response: {str(e)}")

# Clear chat button
if st.button("🔄 Clear Chat History", use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("← Back", use_container_width=True):
        st.switch_page("pages/4_Reports.py")
with col2:
    st.empty()
with col3:
    if st.button("→ Restart Demo", type="primary", use_container_width=True):
        st.switch_page("pages/1_Upload_Tender.py")
