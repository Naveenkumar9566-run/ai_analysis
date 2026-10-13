"""
Authentication Component
Renders the Clerk Sign-In interface, captures session data,
and triggers backend session verification.
"""

import os
import streamlit as st
import streamlit.components.v1 as components
from services.clerk_service import get_clerk_service
from utils.session import authenticate_user, clear_session


# Declare the custom Clerk component from local HTML directory
_COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "clerk_component")
_clerk_auth_component = components.declare_component("clerk_auth_component", path=_COMPONENT_DIR)


def render_clerk_frontend(publishable_key: str, action: str = "render"):
    """Render the embedded ClerkJS component inside Streamlit."""
    return _clerk_auth_component(
        publishable_key=publishable_key,
        action=action,
        key="clerk_frontend_auth"
    )


def show_sign_in_page() -> None:
    """Render the complete Clerk Sign-In Screen."""
    clerk = get_clerk_service()

    # Styling for the Sign-In page
    st.markdown(
        """
        <style>
        .auth-header {
            text-align: center;
            margin-top: 1.5rem;
            margin-bottom: 2rem;
        }
        .auth-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.4);
            color: #818cf8;
            padding: 4px 14px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        .auth-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        .auth-subtitle {
            font-size: 15px;
            color: #94a3b8;
            max-width: 460px;
            margin: 0 auto;
            line-height: 1.5;
        }
        .config-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            margin: 20px auto;
            max-width: 580px;
        }
        .feature-pill {
            display: inline-block;
            background: #0f172a;
            border: 1px solid #334155;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            color: #cbd5e1;
            margin: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Header section
    st.markdown(
        """
        <div class="auth-header">
            <div class="auth-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/>
                </svg>
                Identity by Clerk
            </div>
            <h1 class="auth-title">Clerk Authentication</h1>
            <p class="auth-subtitle">
                Welcome to Clerk Authentication. Sign in below to access your secure profile and protected dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display any active auth errors from previous attempts
    auth_err = st.session_state.get("auth_error")
    if auth_err:
        st.error(f"⚠️ {auth_err}")
        if st.button("Dismiss", key="dismiss_auth_error"):
            st.session_state.auth_error = None
            st.rerun()

    # Check if Clerk keys are properly configured
    if not clerk.is_configured():
        render_configuration_guide(clerk)
        return

    # Two-column layout for centered card
    col1, col2, col3 = st.columns([1, 2.2, 1])

    with col2:
        # Render the Clerk Sign-In component
        tab_component, tab_portal, tab_direct = st.tabs([
            "🔐 Clerk Sign-In",
            "🌐 Hosted Portal",
            "⚡ Direct Session / Token"
        ])

        with tab_component:
            comp_value = render_clerk_frontend(publishable_key=clerk.publishable_key)

            # Check if component returned authenticated state
            if comp_value and isinstance(comp_value, dict):
                if comp_value.get("status") == "authenticated":
                    session_id = comp_value.get("session_id")
                    session_token = comp_value.get("session_token")
                    user_id = comp_value.get("user_id")

                    if session_id:
                        with st.spinner("Validating Clerk session securely..."):
                            success, err = authenticate_user(
                                session_id=session_id,
                                session_token=session_token,
                                user_id=user_id
                            )
                            if success:
                                st.success("Authentication validated! Redirecting...")
                                st.rerun()
                            else:
                                st.error(f"Validation failed: {err}")

        with tab_portal:
            st.markdown(
                """
                <div style="background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 20px; text-align: center; margin-top: 10px;">
                    <p style="color: #cbd5e1; font-size: 14px; margin-bottom: 16px;">
                        Alternatively, you can sign in directly via Clerk's Hosted Account Portal:
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            hosted_url = clerk.get_hosted_sign_in_url()
            st.link_button(
                "🚀 Open Clerk Hosted Sign-In",
                hosted_url,
                use_container_width=True,
                type="primary"
            )
            st.info("After completing sign-in on Clerk, copy your active Session ID (`sess_...`) or session token below to validate.")

        with tab_direct:
            st.markdown(
                """
                <p style="font-size: 13px; color: #94a3b8; margin-bottom: 12px;">
                    Validate an active Clerk Session ID or JWT Session Token directly against the Clerk Backend API:
                </p>
                """,
                unsafe_allow_html=True,
            )

            with st.form("direct_session_form"):
                sess_input = st.text_input(
                    "Clerk Session ID",
                    placeholder="sess_2b...",
                    help="Active Clerk Session ID from Clerk dashboard or client."
                )
                tok_input = st.text_area(
                    "Clerk JWT Session Token (Optional)",
                    placeholder="eyJhbGciOiJSUzI1NiIs...",
                    help="Session token generated by Clerk."
                )
                submitted = st.form_submit_button("Verify & Sign In", type="primary", use_container_width=True)

                if submitted:
                    if not sess_input:
                        st.warning("Please provide a Clerk Session ID.")
                    else:
                        with st.spinner("Validating with Clerk API..."):
                            success, err = authenticate_user(
                                session_id=sess_input.strip(),
                                session_token=tok_input.strip() if tok_input else None
                            )
                            if success:
                                st.success("Session verified! Redirecting to dashboard...")
                                st.rerun()
                            else:
                                st.error(f"Validation failed: {err}")


def render_configuration_guide(clerk: ClerkService) -> None:
    """Displays setup instructions when Clerk keys are missing or invalid."""
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        st.warning("⚠️ **Clerk API Credentials Required**")

        st.markdown(
            """
            To use Clerk Authentication, add your Clerk keys to the `.env` file in the project root:

            ```bash
            CLERK_PUBLISHABLE_KEY=pk_test_...
            CLERK_SECRET_KEY=sk_test_...
            ```

            ### How to get your Clerk keys:
            1. Go to [Clerk Dashboard](https://dashboard.clerk.com) and sign in.
            2. Select your application (or create a new free application).
            3. In the sidebar, navigate to **Configure > Developers > API Keys**.
            4. Copy the **Publishable key** (`pk_test_...`) and **Secret key** (`sk_test_...`).
            5. Paste them into `.env`.
            """
        )

        st.markdown("---")
        st.markdown("#### Quick Test / Set Keys for this Session")

        with st.form("quick_keys_form"):
            pk_val = st.text_input(
                "Clerk Publishable Key",
                value=clerk.publishable_key if clerk.is_publishable_key_valid() else "",
                placeholder="pk_test_...",
                type="default"
            )
            sk_val = st.text_input(
                "Clerk Secret Key",
                value=clerk.secret_key if clerk.is_secret_key_valid() else "",
                placeholder="sk_test_...",
                type="password"
            )
            save_keys = st.form_submit_button("Apply Keys & Reload", type="primary", use_container_width=True)

            if save_keys:
                if pk_val and sk_val:
                    # Update environment and save to .env
                    os.environ["CLERK_PUBLISHABLE_KEY"] = pk_val.strip()
                    os.environ["CLERK_SECRET_KEY"] = sk_val.strip()

                    try:
                        env_path = os.path.join(os.getcwd(), ".env")
                        with open(env_path, "w", encoding="utf-8") as f:
                            f.write(f"CLERK_PUBLISHABLE_KEY={pk_val.strip()}\n")
                            f.write(f"CLERK_SECRET_KEY={sk_val.strip()}\n")
                        st.success("Keys saved to .env! Reloading...")
                    except Exception as e:
                        st.info(f"Keys applied to current session ({str(e)}). Reloading...")

                    st.rerun()
                else:
                    st.error("Please provide both Publishable Key and Secret Key.")
