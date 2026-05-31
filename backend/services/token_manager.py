"""
OAuth2 Token Manager for Microsoft Graph API
Handles token refresh and caching
"""
import msal
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages OAuth2 access tokens with caching"""

    def __init__(self):
        self.token_cache: Dict[str, Dict[str, any]] = {}

    async def get_access_token(
        self,
        client_id: str,
        refresh_token: str,
        email: str
    ) -> Optional[str]:
        """
        Get access token using refresh token

        Args:
            client_id: Azure AD application client ID
            refresh_token: OAuth2 refresh token
            email: User email (used as cache key)

        Returns:
            Access token string or None if failed
        """
        # Check cache first
        if email in self.token_cache:
            cached = self.token_cache[email]
            if datetime.utcnow() < cached["expires_at"]:
                logger.info(f"Using cached token for {email}")
                return cached["token"]
            else:
                logger.info(f"Cached token expired for {email}")

        # Refresh token using MSAL
        try:
            app = msal.PublicClientApplication(
                client_id=client_id,
                authority="https://login.microsoftonline.com/common"
            )

            result = app.acquire_token_by_refresh_token(
                refresh_token=refresh_token,
                scopes=["https://graph.microsoft.com/.default"]
            )

            if "access_token" in result:
                # Cache token (expire 5 minutes early)
                expires_in = result.get("expires_in", 3600)
                self.token_cache[email] = {
                    "token": result["access_token"],
                    "expires_at": datetime.utcnow() + timedelta(seconds=expires_in - 300)
                }
                logger.info(f"Successfully refreshed token for {email}")
                return result["access_token"]
            else:
                error = result.get("error", "unknown_error")
                error_desc = result.get("error_description", "No description")
                logger.error(f"Token refresh failed for {email}: {error} - {error_desc}")
                return None

        except Exception as e:
            logger.error(f"Exception during token refresh for {email}: {str(e)}")
            return None

    def clear_cache(self, email: Optional[str] = None):
        """Clear token cache for specific email or all"""
        if email:
            self.token_cache.pop(email, None)
            logger.info(f"Cleared cache for {email}")
        else:
            self.token_cache.clear()
            logger.info("Cleared all token cache")
