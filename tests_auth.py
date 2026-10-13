"""
Unit and integration tests for Clerk Authentication project.
Tests:
- Service initialization and key validation
- Session management and security gates
- Revocation handling
- Direct session verification flows
"""

import unittest
from unittest.mock import MagicMock, patch
from services.clerk_service import ClerkService
from utils.session import is_authenticated, clear_session, authenticate_user
import streamlit as st


class TestClerkService(unittest.TestCase):
    """Test ClerkService functions and key validations."""

    def test_key_validation(self):
        with patch.dict("os.environ", {
            "CLERK_PUBLISHABLE_KEY": "pk_test_dGVzdC5jbGVyay5hY2NvdW50cy5kZXYk",
            "CLERK_SECRET_KEY": "sk_test_1234567890abcdef"
        }):
            svc = ClerkService()
            self.assertTrue(svc.is_publishable_key_valid())
            self.assertTrue(svc.is_secret_key_valid())
            self.assertTrue(svc.is_configured())
            self.assertEqual(svc.get_frontend_api(), "test.clerk.accounts.dev")

    def test_invalid_key_detection(self):
        with patch.dict("os.environ", {
            "CLERK_PUBLISHABLE_KEY": "pk_test_your_publishable_key_here",
            "CLERK_SECRET_KEY": "sk_test_your_secret_key_here"
        }):
            svc = ClerkService()
            self.assertFalse(svc.is_publishable_key_valid())
            self.assertFalse(svc.is_secret_key_valid())
            self.assertFalse(svc.is_configured())

    def test_session_validation_without_key(self):
        with patch.dict("os.environ", {
            "CLERK_PUBLISHABLE_KEY": "",
            "CLERK_SECRET_KEY": ""
        }):
            svc = ClerkService()
            ok, data, err = svc.validate_session("sess_123")
            self.assertFalse(ok)
            self.assertIn("Secret Key is not configured", err)

    def test_session_revocation(self):
        with patch.dict("os.environ", {
            "CLERK_PUBLISHABLE_KEY": "pk_test_sample",
            "CLERK_SECRET_KEY": "sk_test_sample"
        }):
            svc = ClerkService()
            mock_clerk = MagicMock()
            svc._client = mock_clerk
            mock_clerk.sessions.revoke.return_value = MagicMock()

            ok, err = svc.revoke_session("sess_abc")
            self.assertTrue(ok)
            self.assertIsNone(err)
            mock_clerk.sessions.revoke.assert_called_once_with(session_id="sess_abc")


class TestSessionGate(unittest.TestCase):
    """Test that unauthorized users are rejected and session state alone is not trusted."""

    def setUp(self):
        clear_session()

    def test_unauthenticated_by_default(self):
        self.assertFalse(is_authenticated())

    def test_tampered_session_state_rejected(self):
        # Setting authenticated boolean without valid Clerk session must fail
        st.session_state.authenticated = True
        st.session_state.session_id = None
        st.session_state.user = None
        self.assertFalse(is_authenticated())

    def test_expired_session_handling(self):
        st.session_state.authenticated = True
        st.session_state.session_id = "sess_test"
        # Expired in past
        st.session_state.user = {
            "id": "user_test",
            "session_expire_at": 1000 # epoch millisecond in 1970
        }
        self.assertFalse(is_authenticated())
        self.assertIn("expired", st.session_state.get("auth_error", ""))


if __name__ == "__main__":
    unittest.main()
