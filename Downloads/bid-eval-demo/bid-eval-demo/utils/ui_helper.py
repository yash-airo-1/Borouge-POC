"""UI helper functions for Airo Bid Evaluation Platform."""

from pathlib import Path

import streamlit as st
from utils.state import (
    clear_all_data,
    get_api_key,
    set_api_key,
    get_tender_data,
    get_supplier_evaluations,
)

# Logo path relative to this file so it works locally and on Streamlit Cloud
_LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "AiroLogo.png"


def setup_sidebar():
    """Setup sidebar with logo, API key input, and navigation."""
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
        else:
            import os
            if not os.getenv("ANTHROPIC_API_KEY"):
                st.warning(
                    "⚠️ No API key detected. Please enter one above or set ANTHROPIC_API_KEY environment variable."
                )

        st.markdown("---")

        # Navigation
        st.markdown("### 📍 Navigation")

        pages = [
            "1_Upload_Tender",
            "2_Upload_Bids",
            "3_Dashboard",
            "4_Reports",
            "5_Chat",
        ]

        # Determine current page from session state or default to page 0
        if "current_nav_page" not in st.session_state:
            st.session_state.current_nav_page = "1_Upload_Tender"

        current_index = pages.index(st.session_state.current_nav_page) if st.session_state.current_nav_page in pages else 0

        page = st.radio(
            "Select Page:",
            pages,
            index=current_index,
            format_func=lambda x: {
                "1_Upload_Tender": "📄 Upload Tender",
                "2_Upload_Bids": "📋 Upload Bids",
                "3_Dashboard": "📊 Dashboard",
                "4_Reports": "📑 Reports",
                "5_Chat": "💬 Chat",
            }.get(x, x),
        )

        # Update session state with current page
        st.session_state.current_nav_page = page

        st.markdown("---")

        # Session State Summary
        st.markdown("### 📈 Session Status")

        if get_tender_data():
            st.success("✓ Tender loaded")
        else:
            st.info("○ No tender loaded")

        bid_count = len(get_supplier_evaluations())
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

        return page
