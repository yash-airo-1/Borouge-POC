import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from utils.state import init_session_state, clear_all_data, set_api_key, get_api_key

# Logo path relative to app root so it works locally and on Streamlit Cloud
_LOGO_PATH = Path(__file__).resolve().parent / "assets" / "AiroLogo.png"

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Airo Bid Evaluation Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    :root {
        --primary-color: #E63028;
        --secondary-color: #1A1A1A;
        --background-color: #F5F5F5;
    }

    .main {
        padding: 2rem;
    }

    .stTabs [role="tablist"] {
        gap: 2px;
    }

    .stTabs [role="tab"][aria-selected="true"] {
        color: #E63028;
        border-bottom: 3px solid #E63028;
    }

    h1 {
        color: #1A1A1A;
    }

    h2 {
        color: #E63028;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
init_session_state()

# Sidebar
with st.sidebar:
    # Display Airo Logo
    try:
        st.image(str(_LOGO_PATH), use_container_width=True)
    except Exception:
        # Fallback if image not found
        st.markdown(
            """
            <div style="text-align: center; padding: 20px; background-color: #E63028; border-radius: 10px;">
                <h2 style="color: white; margin: 0;">AIRO</h2>
                <p style="color: white; font-size: 12px; margin: 0;">Digital Labs</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # API Key Management
    st.markdown("### ⚙️ Configuration")

    api_key_input = st.text_input(
        "Anthropic API Key",
        value=get_api_key() or "",
        type="password",
        help="Enter your Anthropic API key. Stored in session only.",
    )

    if api_key_input:
        set_api_key(api_key_input)
        st.success("✓ API Key configured")
    elif not os.getenv("ANTHROPIC_API_KEY"):
        st.warning("⚠️ No API key detected. Please enter one above or set ANTHROPIC_API_KEY environment variable.")

    st.markdown("---")

    # Navigation
    st.markdown("### 📍 Navigation")

    page = st.radio(
        "Select Page:",
        [
            "1_Upload_Tender",
            "2_Upload_Bids",
            "3_Dashboard",
            "4_Reports",
            "5_Chat",
        ],
        index=0,
        format_func=lambda x: {
            "1_Upload_Tender": "📄 Upload Tender",
            "2_Upload_Bids": "📋 Upload Bids",
            "3_Dashboard": "📊 Dashboard",
            "4_Reports": "📑 Reports",
            "5_Chat": "💬 Chat",
        }.get(x, x),
    )

    st.markdown("---")

    # Session State Summary
    st.markdown("### 📈 Session Status")

    if st.session_state.tender_data:
        st.success("✓ Tender loaded")
    else:
        st.info("○ No tender loaded")

    bid_count = len(st.session_state.supplier_evaluations)
    if bid_count > 0:
        st.success(f"✓ {bid_count} bid(s) evaluated")
    else:
        st.info("○ No bids evaluated")

    st.markdown("---")

    # Reset Button
    if st.button("🔄 Reset Demo", use_container_width=True, type="secondary"):
        clear_all_data()
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <p style="font-size: 12px; color: #888; text-align: center;">
        Built by Airo Digital Labs using Anthropic Claude API
        </p>
        """,
        unsafe_allow_html=True,
    )


# Store current page in session state to prevent jumping
if "current_page" not in st.session_state:
    st.session_state.current_page = "1_Upload_Tender"

# Update session state when user selects a different page
if page != st.session_state.current_page:
    st.session_state.current_page = page

# Route to the appropriate page
if st.session_state.current_page == "1_Upload_Tender":
    st.switch_page("pages/1_Upload_Tender.py")
elif st.session_state.current_page == "2_Upload_Bids":
    st.switch_page("pages/2_Upload_Bids.py")
elif st.session_state.current_page == "3_Dashboard":
    st.switch_page("pages/3_Dashboard.py")
elif st.session_state.current_page == "4_Reports":
    st.switch_page("pages/4_Reports.py")
elif st.session_state.current_page == "5_Chat":
    st.switch_page("pages/5_Chat.py")
