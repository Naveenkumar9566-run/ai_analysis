"""
Sidebar Component
Renders the navigation menu, authenticated user badge, and working Sign Out button.
"""

import streamlit as st
from utils.session import get_current_user, sign_out


def render_sidebar() -> str:
    """
    Renders the protected application sidebar.
    Returns the currently selected view ('home', 'dashboard', or 'profile').
    """
    user = get_current_user() or {}

    with st.sidebar:
        # App Branding Header
        st.markdown(
            """
            <div style="padding: 10px 0 20px 0; border-bottom: 1px solid #334155;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <div style="width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">
                        C
                    </div>
                    <div>
                        <div style="font-weight: 700; font-size: 17px; color: #f8fafc; line-height: 1.2;">
                            Clerk Authentication
                        </div>
                        <div style="font-size: 11px; color: #38bdf8; font-weight: 500;">
                            ● Session Authenticated
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Navigation Menu
        views = {
            "🏠 Home": "home",
            "📊 Dashboard": "dashboard",
            "👤 Profile": "profile",
        }

        current_view = st.session_state.get("current_view", "home")
        view_keys = list(views.keys())

        # Determine index
        selected_index = 0
        for idx, (label, view_code) in enumerate(views.items()):
            if view_code == current_view:
                selected_index = idx
                break

        selected_label = st.radio(
            "Navigation",
            options=view_keys,
            index=selected_index,
            label_visibility="collapsed"
        )
        selected_view = views[selected_label]
        st.session_state.current_view = selected_view

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Authenticated User Info Card
        full_name = user.get("full_name", "User")
        email = user.get("email", "")
        img_url = user.get("image_url") or "https://www.gravatar.com/avatar/?d=mp"
        session_id = user.get("session_id", "N/A")

        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 14px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <img src="{img_url}" style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover; border: 2px solid #6366f1;" />
                    <div style="overflow: hidden;">
                        <div style="font-weight: 600; font-size: 14px; color: #f8fafc; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">
                            {full_name}
                        </div>
                        <div style="font-size: 12px; color: #94a3b8; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">
                            {email or "Authenticated"}
                        </div>
                    </div>
                </div>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #334155; font-size: 11px; color: #64748b;">
                    Session: <code style="color: #cbd5e1; font-size: 10px;">{session_id[:16]}...</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Sign Out Section
        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            with st.spinner("Ending Clerk session..."):
                sign_out()

        # Footer info
        st.markdown(
            """
            <div style="font-size: 11px; color: #64748b; text-align: center; margin-top: 20px;">
                Protected by Clerk Backend API & JWKS
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_view
