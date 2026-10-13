"""
Clerk Authentication - Main Application Entrypoint
Project Name: Clerk Authentication

Enforces the authentication flow:
Start Application -> Check Authentication -> (Not Logged In: Show Sign-In) / (Logged In: Show Home Dashboard)
"""

import streamlit as st
from utils.session import init_session_state, is_authenticated
from components.auth import show_sign_in_page
from components.sidebar import render_sidebar
from components.dashboard import show_dashboard
from pages.profile import show_profile_page


def configure_app():
    """Configure main Streamlit app settings and global styling."""
    st.set_page_config(
        page_title="Clerk Authentication",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Global custom styling
    st.markdown(
        """
        <style>
        /* Base typography and smooth layout */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Hide Streamlit default main menu hamburger and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}

        /* Card and metric enhancements */
        div[data-testid="stMetricValue"] {
            font-size: 26px !important;
            font-weight: 700 !important;
            color: #f8fafc !important;
        }

        /* Buttons styling */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out !important;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
        }

        /* Code block improvements */
        code {
            border-radius: 4px !important;
            padding: 2px 6px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    """Main application lifecycle controller."""
    configure_app()
    init_session_state()

    # Step 1: Check Clerk Authentication
    if not is_authenticated():
        # User is NOT logged in: show the Clerk Sign-In screen
        show_sign_in_page()
        return

    # Step 2: User is logged in with validated Clerk session: show protected app
    selected_view = render_sidebar()

    if selected_view == "profile":
        show_profile_page()
    elif selected_view == "dashboard" or selected_view == "home":
        show_dashboard()
    else:
        show_dashboard()


if __name__ == "__main__":
    main()
