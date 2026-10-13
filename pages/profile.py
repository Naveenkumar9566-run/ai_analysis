"""
Profile Page (Protected)
Must require successful Clerk authentication before rendering.
Displays full user profile information fetched from Clerk Backend API.
"""

import streamlit as st
from utils.session import require_auth, get_current_user, sign_out
from components.sidebar import render_sidebar
from services.clerk_service import get_clerk_service


def show_profile_page():
    """Render the protected Profile page."""
    # Enforce Clerk authentication gate
    user = require_auth()

    # Render navigation sidebar
    render_sidebar()

    full_name = user.get("full_name", "User")
    email = user.get("email", "N/A")
    img_url = user.get("image_url") or "https://www.gravatar.com/avatar/?d=mp"
    user_id = user.get("id", "N/A")
    username = user.get("username") or "None set"
    created_at = user.get("created_at", "N/A")
    last_sign_in = user.get("last_sign_in_at", "N/A")
    mfa_enabled = user.get("two_factor_enabled", False)
    all_emails = user.get("all_emails", [])
    if not all_emails and email:
        all_emails = [email]

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); border: 1px solid #3730a3; border-radius: 16px; padding: 28px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 24px; flex-wrap: wrap;">
                <img src="{img_url}" style="width: 88px; height: 88px; border-radius: 50%; object-fit: cover; border: 3px solid #818cf8; box-shadow: 0 4px 16px rgba(0,0,0,0.5);" />
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                        <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: #f8fafc;">
                            {full_name}
                        </h1>
                        <span style="background: rgba(34, 197, 94, 0.2); border: 1px solid rgba(34, 197, 94, 0.4); color: #4ade80; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 600;">
                            Verified
                        </span>
                    </div>
                    <p style="margin: 0; color: #94a3b8; font-size: 14px;">
                        @{username} &bull; Clerk ID: <code style="color: #cbd5e1;">{user_id}</code>
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📧 Email Addresses")
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
                {''.join([f'''
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #334155;">
                    <div>
                        <div style="color: #f8fafc; font-weight: 500;">{em}</div>
                        <div style="font-size: 11px; color: #64748b;">{"Primary Email" if em == email else "Secondary Email"}</div>
                    </div>
                    <span style="background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Verified</span>
                </div>
                ''' for em in all_emails])}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🔐 Security & Multi-Factor Authentication")
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #334155;">
                    <div>
                        <div style="color: #f8fafc; font-weight: 500;">Two-Factor Authentication (2FA)</div>
                        <div style="font-size: 11px; color: #64748b;">Extra protection requiring an authentication app or SMS</div>
                    </div>
                    <span style="background: {'rgba(34, 197, 94, 0.15)' if mfa_enabled else 'rgba(234, 179, 8, 0.15)'}; color: {'#4ade80' if mfa_enabled else '#facc15'}; padding: 2px 8px; border-radius: 4px; font-size: 11px;">
                        {'Enabled' if mfa_enabled else 'Disabled'}
                    </span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 0;">
                    <div>
                        <div style="color: #f8fafc; font-weight: 500;">Session Authentication Protocol</div>
                        <div style="font-size: 11px; color: #64748b;">Protected via Clerk Cryptographic JWT tokens and live backend validation</div>
                    </div>
                    <span style="background: rgba(99, 102, 241, 0.15); color: #a5b4fc; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Active</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("### ℹ️ Account Overview")
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
                <div style="margin-bottom: 12px;">
                    <span style="font-size: 12px; color: #94a3b8;">Created On:</span>
                    <div style="color: #f8fafc; font-weight: 600; font-size: 13px;">{created_at}</div>
                </div>
                <div style="margin-bottom: 12px;">
                    <span style="font-size: 12px; color: #94a3b8;">Last Sign In:</span>
                    <div style="color: #f8fafc; font-weight: 600; font-size: 13px;">{last_sign_in}</div>
                </div>
                <div>
                    <span style="font-size: 12px; color: #94a3b8;">Session Status:</span>
                    <div style="color: #4ade80; font-weight: 600; font-size: 13px;">Active & Verified</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🔄 Refresh Profile from Clerk", use_container_width=True):
            with st.spinner("Fetching updated profile from Clerk API..."):
                clerk = get_clerk_service()
                ok, profile, err = clerk.get_user_profile(user_id)
                if ok and profile:
                    st.session_state.user.update(profile)
                    st.success("Profile refreshed!")
                    st.rerun()
                else:
                    st.error(f"Failed to refresh: {err}")

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            sign_out()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Profile - Clerk Authentication",
        page_icon="👤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    show_profile_page()
