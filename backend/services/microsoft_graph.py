"""
Microsoft Graph API Client
Handles email retrieval from Outlook/Hotmail
"""
import httpx
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MicrosoftGraphClient:
    """Client for Microsoft Graph API"""

    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def get_last_emails(
        self,
        email: str,
        num: int = 1,
        box_type: int = 1
    ) -> List[Dict]:
        """
        Get last N emails from inbox or junk folder

        Args:
            email: User email address
            num: Number of emails to retrieve (1-5)
            box_type: 1 for inbox, 2 for junk

        Returns:
            List of email dictionaries
        """
        # Determine folder
        folder = "inbox" if box_type == 1 else "junkemail"

        # Build API request
        url = f"{self.BASE_URL}/users/{email}/mailFolders/{folder}/messages"
        params = {
            "$top": min(num, 5),
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,toRecipients,receivedDateTime,bodyPreview,body,hasAttachments,isRead"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Fetching {num} emails from {folder} for {email}")
                response = await client.get(url, headers=self.headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    messages = data.get("value", [])
                    logger.info(f"Successfully retrieved {len(messages)} emails")
                    return self._format_emails(messages)
                else:
                    logger.error(f"Graph API error: {response.status_code} - {response.text}")
                    return []

        except httpx.TimeoutException:
            logger.error(f"Timeout while fetching emails for {email}")
            return []
        except Exception as e:
            logger.error(f"Exception while fetching emails: {str(e)}")
            return []

    def _format_emails(self, messages: List[Dict]) -> List[Dict]:
        """Format Graph API response to match expected output"""
        result = []
        for msg in messages:
            # Extract from field
            from_field = msg.get("from", {}).get("emailAddress", {})

            # Extract to field
            to_recipients = msg.get("toRecipients", [])
            to_address = to_recipients[0].get("emailAddress", {}).get("address", "") if to_recipients else ""
            to_name = to_recipients[0].get("emailAddress", {}).get("name", "") if to_recipients else ""

            # Extract body
            body_obj = msg.get("body", {})
            body_content = body_obj.get("content", "")
            body_type = body_obj.get("contentType", "text")

            # Format date
            received_dt = msg.get("receivedDateTime", "")

            result.append({
                "Date": received_dt.replace("T", " ").replace("Z", ""),
                "From": f"{from_field.get('name', '')} <{from_field.get('address', '')}>",
                "To": f"{to_name} <{to_address}>",
                "Subject": msg.get("subject", ""),
                "Body": body_content,
                "BodyPreview": msg.get("bodyPreview", ""),
                "HasAttachments": msg.get("hasAttachments", False),
                "IsRead": msg.get("isRead", False)
            })

        return result
