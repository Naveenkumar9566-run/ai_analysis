"""
Home Page (Protected)
Must require successful Clerk authentication before rendering.
"""

import streamlit as st
from utils.session import require_auth
from components.sidebar import render_sidebar
from components.dashboard import show_dashboard


def show_home_page():
    """Render the protected Home page."""
    # Enforce Clerk authentication gate
    user = require_auth()

    # Render navigation sidebar
    selected_view = render_sidebar()

    # Route according to sidebar selection if visited directly
    if selected_view == "profile":
        from pages.profile import show_profile_page
        show_profile_page()
    else:
        show_dashboard()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Home - Clerk Authentication",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    show_home_page()
