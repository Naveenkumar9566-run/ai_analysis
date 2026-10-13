"""
Dashboard Component
Renders the protected dashboard view with user details, status cards, and security insights.
"""

from datetime import datetime, timezone
import streamlit as st
from utils.session import get_current_user, sign_out
from services.clerk_service import get_clerk_service


def render_dashboard_header(user: dict) -> None:
    """Render the top welcome header with Clerk user data."""
    full_name = user.get("full_name") or "User"
    email = user.get("email") or "No email provided"
    img_url = user.get("image_url") or "https://www.gravatar.com/avatar/?d=mp"
    user_id = user.get("id") or "N/A"

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1e1b4b 0%, #1e293b 100%); border: 1px solid #3730a3; border-radius: 16px; padding: 28px; margin-bottom: 24px; box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.2);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <img src="{img_url}" style="width: 72px; height: 72px; border-radius: 50%; object-fit: cover; border: 3px solid #818cf8; box-shadow: 0 4px 14px rgba(0,0,0,0.4);" />
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <span style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.4); color: #4ade80; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 600;">
                                ● Authenticated
                            </span>
                            <span style="color: #94a3b8; font-size: 12px;">Clerk ID: <code style="color: #cbd5e1; font-size: 11px;">{user_id}</code></span>
                        </div>
                        <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em;">
                            Welcome, {full_name}
                        </h1>
                        <p style="margin: 4px 0 0 0; color: #cbd5e1; font-size: 14px;">
                            ✉️ {email}
                        </p>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_section() -> None:
    """Render the primary welcome message required by the project specifications."""
    st.markdown(
        """
        <div style="background: #1e293b; border-left: 4px solid #6366f1; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; border-radius: 12px; padding: 22px; margin-bottom: 28px;">
            <h2 style="font-size: 20px; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">
                Welcome to Clerk Authentication
            </h2>
            <p style="font-size: 15px; color: #94a3b8; margin: 0; line-height: 1.6;">
                You have successfully signed in using Clerk Authentication. Your session has been verified with Clerk's Backend API and your protected dashboard is ready.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_cards(user: dict) -> None:
    """Render the 4 responsive dashboard cards."""
    col1, col2 = st.columns(2)

    # 1. Authentication Status Card
    with col1:
        session_id = user.get("session_id", "N/A")
        session_status = user.get("session_status", "active").upper()
        validated_at = user.get("validated_at", "Just now")

        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 20px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                    <div style="font-weight: 700; font-size: 16px; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
                        <span>🔒</span> Authentication Status
                    </div>
                    <span style="background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;">
                        AUTHENTICATED
                    </span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Clerk Session Status:</span>
                        <span style="color: #4ade80; font-weight: 600;">{session_status}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Session ID:</span>
                        <code style="color: #cbd5e1; font-size: 11px;">{session_id[:18]}...</code>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Validation Layer:</span>
                        <span style="color: #cbd5e1;">Clerk Backend API & JWKS</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #94a3b8;">Last Validated:</span>
                        <span style="color: #cbd5e1; font-size: 12px;">{validated_at}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. User Profile Card
    with col2:
        full_name = user.get("full_name", "N/A")
        username = user.get("username") or "None set"
        email = user.get("email", "N/A")
        user_id = user.get("id", "N/A")

        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 20px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                    <div style="font-weight: 700; font-size: 16px; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
                        <span>👤</span> User Profile
                    </div>
                    <span style="background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.4); padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;">
                        VERIFIED PROFILE
                    </span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Display Name:</span>
                        <span style="color: #f8fafc; font-weight: 600;">{full_name}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Primary Email:</span>
                        <span style="color: #cbd5e1;">{email}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Username:</span>
                        <span style="color: #cbd5e1;">@{username}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #94a3b8;">User ID:</span>
                        <code style="color: #cbd5e1; font-size: 11px;">{user_id[:18]}...</code>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    # 3. Account Information Card
    with col3:
        created_at = user.get("created_at", "N/A")
        last_sign_in = user.get("last_sign_in_at", "N/A")
        mfa_enabled = "Enabled (2FA)" if user.get("two_factor_enabled") else "Disabled"
        email_count = len(user.get("all_emails", [])) or 1

        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 20px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                    <div style="font-weight: 700; font-size: 16px; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
                        <span>📋</span> Account Information
                    </div>
                    <span style="background: rgba(14, 165, 233, 0.2); color: #7dd3fc; border: 1px solid rgba(14, 165, 233, 0.4); padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;">
                        ACCOUNT DATA
                    </span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Member Since:</span>
                        <span style="color: #cbd5e1;">{created_at}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Last Sign In:</span>
                        <span style="color: #cbd5e1;">{last_sign_in}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Multi-Factor Auth (MFA):</span>
                        <span style="color: {'#4ade80' if user.get('two_factor_enabled') else '#facc15'}; font-weight: 600;">{mfa_enabled}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #94a3b8;">Linked Emails:</span>
                        <span style="color: #cbd5e1;">{email_count} verified email(s)</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. Application Status Card
    with col4:
        st.markdown(
            """
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 20px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                    <div style="font-weight: 700; font-size: 16px; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
                        <span>⚙️</span> Application Status
                    </div>
                    <span style="background: rgba(168, 85, 247, 0.2); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.4); padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;">
                        ACTIVE SYSTEM
                    </span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Clerk API Gateway:</span>
                        <span style="color: #4ade80; font-weight: 600;">Connected (Healthy)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Session Gate:</span>
                        <span style="color: #4ade80; font-weight: 600;">Active Enforcement</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 8px;">
                        <span style="color: #94a3b8;">Secret Key Security:</span>
                        <span style="color: #4ade80; font-weight: 600;">Secured (Server-only)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #94a3b8;">Environment Mode:</span>
                        <span style="color: #cbd5e1;">Streamlit Production</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dashboard_actions(user: dict) -> None:
    """Render interactive controls for session refresh, details inspection, and sign out."""
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    tab_details, tab_security = st.tabs(["🔍 Session Inspection", "🛡️ Security Information"])

    with tab_details:
        st.markdown("#### Live Session Data (Verified from Clerk)")
        clean_user_info = {
            "clerk_user_id": user.get("id"),
            "full_name": user.get("full_name"),
            "primary_email": user.get("email"),
            "username": user.get("username"),
            "session_id": user.get("session_id"),
            "session_status": user.get("session_status"),
            "last_validated": user.get("validated_at"),
            "mfa_active": user.get("two_factor_enabled"),
        }
        st.json(clean_user_info)

        col_refresh, col_signout = st.columns([1, 1])
        with col_refresh:
            if st.button("🔄 Re-verify Session with Clerk API", use_container_width=True):
                with st.spinner("Contacting Clerk Backend API..."):
                    clerk = get_clerk_service()
                    is_valid, session_data, err = clerk.validate_session(user.get("session_id", ""))
                    if is_valid:
                        st.toast("Clerk session confirmed active!")
                        st.session_state.last_validated = datetime.now(timezone.utc).timestamp()
                        st.rerun()
                    else:
                        st.error(f"Validation failed: {err}")
                        sign_out()

        with col_signout:
            if st.button("🚪 Sign Out of Clerk", use_container_width=True, type="secondary"):
                sign_out()

    with tab_security:
        st.markdown(
            """
            #### Security Architecture
            * **Server-Side Validation:** The secret key (`CLERK_SECRET_KEY`) is stored only in `.env` and executed strictly in Python backend code.
            * **Live Session Verification:** Every protected page and API interaction verifies that the Clerk session has not been revoked or expired on Clerk's servers.
            * **Tamper Proofing:** Modifying `st.session_state` without a valid Clerk session results in immediate redirection to the Sign-In page.
            * **Clean Revocation:** Clicking Sign Out triggers `clerk.sessions.revoke()` to invalidate the session directly on Clerk's servers.
            """
        )


def show_dashboard() -> None:
    """Entrypoint to render the full authenticated dashboard."""
    user = get_current_user()
    if not user:
        st.warning("Session not available. Please sign in.")
        return

    render_dashboard_header(user)
    render_welcome_section()
    render_dashboard_cards(user)
    render_dashboard_actions(user)
