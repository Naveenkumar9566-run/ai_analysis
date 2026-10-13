"""
Session Management Utility
Manages Streamlit session state and enforces Clerk session validation.
"""

import time
from typing import Optional, Dict, Any, Tuple
import streamlit as st
from services.clerk_service import get_clerk_service


# Throttle live backend validation to every 30 seconds to optimize performance while ensuring security
VALIDATION_CACHE_TTL_SECONDS = 30


def init_session_state() -> None:
    """Initialize necessary session state keys if not already present."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "session_id" not in st.session_state:
        st.session_state.session_id = None

    if "session_token" not in st.session_state:
        st.session_state.session_token = None

    if "user" not in st.session_state:
        st.session_state.user = None

    if "last_validated" not in st.session_state:
        st.session_state.last_validated = 0.0

    if "auth_error" not in st.session_state:
        st.session_state.auth_error = None

    if "current_view" not in st.session_state:
        st.session_state.current_view = "home"


def is_authenticated() -> bool:
    """
    Check if the user is authenticated with a VALID, active Clerk session.
    Never relies solely on a simple boolean in st.session_state.
    Validates Clerk session with Clerk's Backend API if cache TTL expired.
    """
    init_session_state()

    session_id = st.session_state.get("session_id")
    user = st.session_state.get("user")

    if not session_id or not user:
        st.session_state.authenticated = False
        return False

    now = time.time()
    last_val = st.session_state.get("last_validated", 0.0)

    # Check expiration timestamp in user object if available
    expire_at = user.get("session_expire_at")
    if expire_at:
        expire_ms = expire_at if expire_at > 1e11 else expire_at * 1000
        if (now * 1000) >= expire_ms:
            # Session expired
            clear_session(error_msg="Your Clerk session has expired. Please sign in again.")
            return False

    # Check if cache expired and we need to re-validate with Clerk backend
    if now - last_val > VALIDATION_CACHE_TTL_SECONDS:
        clerk = get_clerk_service()
        if clerk.is_secret_key_valid():
            is_valid, session_data, err = clerk.validate_session(session_id)
            if not is_valid:
                clear_session(error_msg=f"Session validation failed: {err or 'Session inactive'}")
                return False

            # Refresh validation timestamp
            st.session_state.last_validated = now
            if session_data:
                st.session_state.user["session_status"] = session_data.get("status", "active")

    st.session_state.authenticated = True
    return True


def authenticate_user(
    session_id: str,
    session_token: Optional[str] = None,
    user_id: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Execute full Clerk backend validation and store session data upon success.
    """
    init_session_state()
    clerk = get_clerk_service()

    if not clerk.is_configured():
        msg = "Clerk is not properly configured. Check CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY in .env."
        st.session_state.auth_error = msg
        return False, msg

    is_valid, user_data, error_msg = clerk.validate_and_create_session(
        session_id=session_id,
        session_token=session_token,
        user_id=user_id
    )

    if not is_valid or not user_data:
        err = error_msg or "Authentication failed with Clerk."
        clear_session(error_msg=err)
        return False, err

    # Store verified session
    st.session_state.authenticated = True
    st.session_state.session_id = session_id
    st.session_state.session_token = session_token
    st.session_state.user = user_data
    st.session_state.last_validated = time.time()
    st.session_state.auth_error = None
    return True, None


def clear_session(error_msg: Optional[str] = None) -> None:
    """Clear local Streamlit session state and record any error message."""
    st.session_state.authenticated = False
    st.session_state.session_id = None
    st.session_state.session_token = None
    st.session_state.user = None
    st.session_state.last_validated = 0.0
    st.session_state.auth_error = error_msg


def sign_out() -> None:
    """
    End Clerk session on Clerk servers, clear local session, and reload app.
    """
    init_session_state()
    session_id = st.session_state.get("session_id")

    if session_id:
        clerk = get_clerk_service()
        if clerk.is_secret_key_valid():
            clerk.revoke_session(session_id)

    clear_session()
    # Also set a query param flag or trigger rerun
    st.rerun()


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get verified user dictionary if authenticated."""
    if is_authenticated():
        return st.session_state.get("user")
    return None


def require_auth() -> Dict[str, Any]:
    """
    Authentication guard for protected pages.
    Validates Clerk session before any protected content is displayed.
    If not authenticated, renders the sign-in page and halts script execution.
    """
    if not is_authenticated():
        # Import lazily to avoid circular imports
        from components.auth import show_sign_in_page
        show_sign_in_page()
        st.stop()

    return st.session_state.user
