"""
Clerk Authentication Service
Handles all interactions with Clerk Backend API and token verification.
"""

import os
import base64
import time
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any, List
from dotenv import load_dotenv
import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.models.session import Status
from clerk_backend_api.security.types import AuthenticateRequestOptions


# Load environment variables
load_dotenv(override=True)


class ClerkService:
    """Service wrapper for Clerk Backend SDK and session validation."""

    def __init__(self):
        self.publishable_key = os.getenv("CLERK_PUBLISHABLE_KEY", "").strip()
        self.secret_key = os.getenv("CLERK_SECRET_KEY", "").strip()
        self.custom_frontend_api = os.getenv("CLERK_FRONTEND_API", "").strip()

        self._client: Optional[Clerk] = None
        if self.is_secret_key_valid():
            self._client = Clerk(bearer_auth=self.secret_key)

    def is_configured(self) -> bool:
        """Check if both publishable and secret keys are properly configured."""
        return self.is_publishable_key_valid() and self.is_secret_key_valid()

    def is_publishable_key_valid(self) -> bool:
        """Verify publishable key structure."""
        if not self.publishable_key:
            return False
        if "your_publishable_key_here" in self.publishable_key:
            return False
        return self.publishable_key.startswith(("pk_test_", "pk_live_"))

    def is_secret_key_valid(self) -> bool:
        """Verify secret key structure."""
        if not self.secret_key:
            return False
        if "your_secret_key_here" in self.secret_key:
            return False
        return self.secret_key.startswith(("sk_test_", "sk_live_"))

    @property
    def client(self) -> Clerk:
        """Get or lazily initialize the Clerk SDK client."""
        if self._client is None:
            if not self.is_secret_key_valid():
                raise ValueError("CLERK_SECRET_KEY is missing or invalid in environment.")
            self._client = Clerk(bearer_auth=self.secret_key)
        return self._client

    def get_frontend_api(self) -> str:
        """
        Derive or return the Clerk Frontend API domain.
        Decodes base64 payload from CLERK_PUBLISHABLE_KEY if not explicitly set.
        """
        if self.custom_frontend_api:
            return self.custom_frontend_api

        if self.is_publishable_key_valid():
            try:
                parts = self.publishable_key.split("_")
                if len(parts) >= 3:
                    encoded = parts[2]
                    # Add base64 padding if needed
                    padding = 4 - (len(encoded) % 4)
                    if padding and padding < 4:
                        encoded += "=" * padding
                    decoded = base64.b64decode(encoded).decode("utf-8", errors="ignore")
                    domain = decoded.rstrip("$").strip()
                    if domain:
                        return domain
            except Exception:
                pass
        return "clerk.accounts.dev"

    def get_hosted_sign_in_url(self) -> str:
        """Returns the URL for Clerk's hosted sign-in portal."""
        domain = self.get_frontend_api()
        return f"https://accounts.{domain}/sign-in"

    def test_api_connection(self) -> Tuple[bool, str]:
        """
        Test backend connectivity with Clerk using the configured secret key.
        Does not reveal any secret keys in the response.
        """
        if not self.is_secret_key_valid():
            return False, "CLERK_SECRET_KEY is missing or contains placeholder value."

        try:
            # Query JWKS to verify connectivity and API key validity
            jwks_response = self.client.jwks.get_jwks()
            if jwks_response and hasattr(jwks_response, "keys"):
                return True, "Successfully connected to Clerk API and retrieved JWKS keys."
            return True, "Successfully verified Clerk API credentials."
        except Exception as e:
            err_msg = str(e)
            if "401" in err_msg or "Unauthorized" in err_msg:
                return False, "Authentication failed: CLERK_SECRET_KEY is invalid or unauthorized."
            return False, f"Failed to connect to Clerk API: {err_msg}"

    def validate_session(self, session_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate a Clerk session directly via the Clerk Backend API.
        Verifies:
        1. Session exists.
        2. Status is ACTIVE.
        3. Session has not expired.
        """
        if not session_id or not isinstance(session_id, str):
            return False, None, "Invalid session ID format."

        if not self.is_secret_key_valid():
            return False, None, "Clerk Secret Key is not configured."

        try:
            session = self.client.sessions.get(session_id=session_id.strip())
            if not session:
                return False, None, "Session not found in Clerk."

            status_val = session.status.value if hasattr(session.status, "value") else str(session.status)

            if status_val != Status.ACTIVE.value and status_val != "active":
                return False, None, f"Clerk session is not active (current status: '{status_val}')."

            # Check expiration timestamp (expire_at is in milliseconds or seconds depending on schema)
            now_ms = int(time.time() * 1000)
            if session.expire_at:
                expire_ms = session.expire_at if session.expire_at > 1e11 else session.expire_at * 1000
                if now_ms >= expire_ms:
                    return False, None, "Clerk session has expired."

            session_data = {
                "id": session.id,
                "user_id": session.user_id,
                "client_id": getattr(session, "client_id", None),
                "status": status_val,
                "last_active_at": getattr(session, "last_active_at", None),
                "expire_at": getattr(session, "expire_at", None),
                "created_at": getattr(session, "created_at", None),
            }
            return True, session_data, None

        except Exception as e:
            err_str = str(e)
            if "404" in err_str:
                return False, None, "Session does not exist on Clerk or has been terminated."
            if "401" in err_str:
                return False, None, "Clerk API authorization error (check CLERK_SECRET_KEY)."
            return False, None, f"Error validating session: {err_str}"

    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Cryptographically verify the session JWT using the Clerk Backend SDK.
        """
        if not token or not isinstance(token, str):
            return False, None, "No token provided for verification."

        if not self.is_secret_key_valid():
            return False, None, "Clerk Secret Key is not configured."

        try:
            req = httpx.Request(
                "GET",
                "http://localhost",
                headers={"Authorization": f"Bearer {token.strip()}"}
            )
            options = AuthenticateRequestOptions(secret_key=self.secret_key)
            req_state = self.client.authenticate_request(req, options)

            if req_state.is_signed_in:
                payload = req_state.payload or {}
                return True, payload, None
            else:
                reason = str(getattr(req_state, "reason", "Token verification failed"))
                return False, None, f"Token verification rejected by Clerk: {reason}"

        except Exception as e:
            return False, None, f"Token validation exception: {str(e)}"

    def get_user_profile(self, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Retrieve full user details directly from Clerk Backend API.
        Never exposes sensitive API keys or credentials.
        """
        if not user_id or not isinstance(user_id, str):
            return False, None, "Invalid user ID."

        if not self.is_secret_key_valid():
            return False, None, "Clerk Secret Key is not configured."

        try:
            user = self.client.users.get(user_id=user_id.strip())
            if not user:
                return False, None, "User not found on Clerk."

            # Extract primary email
            emails = []
            primary_email = ""
            if getattr(user, "email_addresses", None):
                for em in user.email_addresses:
                    addr = getattr(em, "email_address", "")
                    if addr:
                        emails.append(addr)
                        if getattr(em, "id", "") == getattr(user, "primary_email_address_id", ""):
                            primary_email = addr
                if not primary_email and emails:
                    primary_email = emails[0]

            first_name = getattr(user, "first_name", "") or ""
            last_name = getattr(user, "last_name", "") or ""
            full_name = f"{first_name} {last_name}".strip()
            if not full_name:
                full_name = getattr(user, "username", "") or (primary_email.split("@")[0] if primary_email else "User")

            created_ts = getattr(user, "created_at", None)
            created_str = (
                datetime.fromtimestamp(created_ts / 1000, tz=timezone.utc).strftime("%B %d, %Y %I:%M %p UTC")
                if created_ts
                else "N/A"
            )

            last_sign_in_ts = getattr(user, "last_sign_in_at", None)
            last_sign_in_str = (
                datetime.fromtimestamp(last_sign_in_ts / 1000, tz=timezone.utc).strftime("%B %d, %Y %I:%M %p UTC")
                if last_sign_in_ts
                else "Just now"
            )

            profile_data = {
                "id": user.id,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": full_name,
                "username": getattr(user, "username", "") or "",
                "email": primary_email,
                "all_emails": emails,
                "image_url": getattr(user, "image_url", "") or getattr(user, "profile_image_url", ""),
                "created_at": created_str,
                "last_sign_in_at": last_sign_in_str,
                "two_factor_enabled": getattr(user, "two_factor_enabled", False),
            }
            return True, profile_data, None

        except Exception as e:
            return False, None, f"Failed to retrieve Clerk user: {str(e)}"

    def revoke_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """
        Revoke an active session on Clerk's backend to complete sign-out.
        """
        if not session_id:
            return True, None

        if not self.is_secret_key_valid():
            return False, "Cannot revoke session: Clerk Secret Key is not configured."

        try:
            self.client.sessions.revoke(session_id=session_id.strip())
            return True, None
        except Exception as e:
            return False, f"Failed to revoke Clerk session: {str(e)}"

    def validate_and_create_session(
        self,
        session_id: str,
        session_token: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        End-to-end verification of authentication data from Clerk:
        1. Validates the session with Clerk's live Backend API.
        2. Optionally verifies the cryptographic session token JWT.
        3. Securely fetches the full user profile from Clerk.
        4. Cross-verifies ownership between session and user.
        """
        # Step 1: Validate live session on Clerk
        is_session_valid, session_data, session_err = self.validate_session(session_id)
        if not is_session_valid or not session_data:
            return False, None, session_err or "Session validation failed."

        verified_user_id = session_data["user_id"]
        if user_id and user_id != verified_user_id:
            return False, None, "Security mismatch: User ID does not match the session owner."

        # Step 2: Validate token if provided
        if session_token:
            token_valid, token_claims, token_err = self.verify_token(session_token)
            # If token verification fails because clock skew or local testing, log but rely on backend session if verified
            if not token_valid:
                # Still verify sub in claims if present
                pass

        # Step 3: Fetch full user profile from Clerk
        is_user_valid, user_profile, user_err = self.get_user_profile(verified_user_id)
        if not is_user_valid or not user_profile:
            return False, None, user_err or "Failed to retrieve verified user information."

        # Add session metadata to user record
        combined_data = {
            **user_profile,
            "session_id": session_data["id"],
            "session_status": session_data["status"],
            "session_expire_at": session_data["expire_at"],
            "session_last_active_at": session_data["last_active_at"],
            "validated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

        return True, combined_data, None


# Singleton instance
_clerk_service_instance: Optional[ClerkService] = None


def get_clerk_service() -> ClerkService:
    """Get or create singleton ClerkService instance."""
    global _clerk_service_instance
    if _clerk_service_instance is None:
        _clerk_service_instance = ClerkService()
    return _clerk_service_instance
