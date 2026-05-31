"""
IMAP Service for Email Retrieval
Alternative implementation using IMAP protocol
"""
import aioimaplib
import email
from email.header import decode_header
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class IMAPService:
    """IMAP service for email retrieval"""

    IMAP_SERVER = "outlook.office365.com"
    IMAP_PORT = 993

    def __init__(self, email_addr: str, password: str):
        self.email_addr = email_addr
        self.password = password
        self.client = None

    async def connect(self) -> bool:
        """Connect to IMAP server"""
        try:
            self.client = aioimaplib.IMAP4_SSL(host=self.IMAP_SERVER, port=self.IMAP_PORT)
            await self.client.wait_hello_from_server()
            logger.info(f"Connected to IMAP server for {self.email_addr}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {str(e)}")
            return False

    async def login(self) -> bool:
        """Login to IMAP server"""
        try:
            response = await self.client.login(self.email_addr, self.password)
            if response.result == "OK":
                logger.info(f"Successfully logged in as {self.email_addr}")
                return True
            else:
                logger.error(f"Login failed: {response}")
                return False
        except Exception as e:
            logger.error(f"Exception during login: {str(e)}")
            return False

    async def get_last_emails(
        self,
        num: int = 1,
        box_type: int = 1
    ) -> List[Dict]:
        """
        Get last N emails from inbox or junk folder

        Args:
            num: Number of emails to retrieve (1-5)
            box_type: 1 for inbox, 2 for junk

        Returns:
            List of email dictionaries
        """
        try:
            # Select folder
            folder = "INBOX" if box_type == 1 else "Junk"
            await self.client.select(folder)
            logger.info(f"Selected folder: {folder}")

            # Search for all messages
            _, msg_ids = await self.client.search("ALL")
            msg_id_list = msg_ids[0].split()

            if not msg_id_list:
                logger.warning(f"No messages found in {folder}")
                return []

            # Get latest N messages
            latest_ids = msg_id_list[-num:]
            logger.info(f"Fetching {len(latest_ids)} messages from {folder}")

            emails = []
            for msg_id in latest_ids:
                email_data = await self._fetch_email(msg_id)
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            logger.error(f"Exception while fetching emails: {str(e)}")
            return []

    async def _fetch_email(self, msg_id: bytes) -> Optional[Dict]:
        """Fetch and parse a single email"""
        try:
            _, msg_data = await self.client.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[1]
            email_message = email.message_from_bytes(raw_email)

            # Extract headers
            subject = self._decode_header(email_message.get("Subject", ""))
            from_addr = self._decode_header(email_message.get("From", ""))
            to_addr = self._decode_header(email_message.get("To", ""))
            date_str = email_message.get("Date", "")

            # Parse date
            try:
                date_obj = email.utils.parsedate_to_datetime(date_str)
                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_date = date_str

            # Extract body
            body_text = ""
            body_html = ""
            body_preview = ""

            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body_text = payload.decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body_html = payload.decode('utf-8', errors='ignore')
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    content_type = email_message.get_content_type()
                    if content_type == "text/plain":
                        body_text = payload.decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        body_html = payload.decode('utf-8', errors='ignore')

            # Generate preview
            body_preview = body_text[:200] if body_text else body_html[:200]

            # Check for attachments
            has_attachments = False
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_disposition() == "attachment":
                        has_attachments = True
                        break

            return {
                "Date": formatted_date,
                "From": from_addr,
                "To": to_addr,
                "Subject": subject,
                "Body": body_html if body_html else body_text,
                "BodyPreview": body_preview,
                "HasAttachments": has_attachments,
                "IsRead": False  # IMAP doesn't easily provide read status
            }

        except Exception as e:
            logger.error(f"Exception while parsing email {msg_id}: {str(e)}")
            return None

    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ""

        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                if encoding:
                    decoded_parts.append(part.decode(encoding, errors='ignore'))
                else:
                    decoded_parts.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded_parts.append(part)

        return "".join(decoded_parts)

    async def logout(self):
        """Logout from IMAP server"""
        try:
            if self.client:
                await self.client.logout()
                logger.info(f"Logged out from {self.email_addr}")
        except Exception as e:
            logger.error(f"Exception during logout: {str(e)}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.logout()
