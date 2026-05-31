import aioimaplib
import email
from email.header import decode_header
from datetime import datetime
from typing import List, Dict, Optional
import asyncio


class IMAPClient:
    def __init__(self, email_address: str, token: str, server: str = "outlook.office365.com", port: int = 993):
        self.email = email_address
        self.token = token
        self.server = server
        self.port = port
        self.client: Optional[aioimaplib.IMAP4_SSL] = None

    async def connect(self):
        """连接到 IMAP 服务器"""
        try:
            self.client = aioimaplib.IMAP4_SSL(host=self.server, port=self.port)
            await self.client.wait_hello_from_server()

            # 使用 OAuth2 令牌登录
            await self.client.login(self.email, self.token)
            await self.client.select('INBOX')
            return True
        except Exception as e:
            print(f"IMAP 连接失败 {self.email}: {e}")
            return False

    async def fetch_new_emails(self, limit: int = 50) -> List[Dict]:
        """获取新邮件"""
        if not self.client:
            await self.connect()

        try:
            # 搜索最近的邮件
            status, messages = await self.client.search('ALL')
            if status != 'OK':
                return []

            email_ids = messages[0].split()
            # 获取最新的 N 封邮件
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids

            emails = []
            for email_id in reversed(email_ids):  # 从新到旧
                email_data = await self.fetch_email(email_id.decode())
                if email_data:
                    emails.append(email_data)

            return emails
        except Exception as e:
            print(f"获取邮件失败 {self.email}: {e}")
            return []

    async def fetch_email(self, email_id: str) -> Optional[Dict]:
        """获取单封邮件详情"""
        try:
            status, msg_data = await self.client.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return None

            # 解析邮件
            raw_email = msg_data[1]
            msg = email.message_from_bytes(raw_email)

            # 解码邮件头
            subject = self._decode_header(msg.get('Subject', ''))
            sender = self._decode_header(msg.get('From', ''))
            recipient = self._decode_header(msg.get('To', ''))
            date_str = msg.get('Date', '')
            message_id = msg.get('Message-ID', '')

            # 解析日期
            try:
                date = email.utils.parsedate_to_datetime(date_str)
            except:
                date = datetime.utcnow()

            # 提取邮件正文
            body_text, body_html = self._extract_body(msg)

            # 检查附件
            has_attachments = any(part.get_content_disposition() == 'attachment' for part in msg.walk())

            return {
                'message_id': message_id,
                'subject': subject,
                'sender': sender,
                'recipient': recipient,
                'date': date,
                'body_text': body_text,
                'body_html': body_html,
                'has_attachments': has_attachments,
                'raw_headers': str(msg)
            }
        except Exception as e:
            print(f"解析邮件失败 {email_id}: {e}")
            return None

    def _decode_header(self, header: str) -> str:
        """解码邮件头"""
        if not header:
            return ""

        decoded_parts = decode_header(header)
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(encoding or 'utf-8', errors='ignore'))
            else:
                result.append(part)
        return ''.join(result)

    def _extract_body(self, msg) -> tuple:
        """提取邮件正文（纯文本和 HTML）"""
        body_text = ""
        body_html = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = part.get_content_disposition()

                if content_disposition == 'attachment':
                    continue

                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        decoded = payload.decode(charset, errors='ignore')

                        if content_type == 'text/plain' and not body_text:
                            body_text = decoded
                        elif content_type == 'text/html' and not body_html:
                            body_html = decoded
                except Exception as e:
                    print(f"解析邮件正文失败: {e}")
        else:
            content_type = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    decoded = payload.decode(charset, errors='ignore')

                    if content_type == 'text/plain':
                        body_text = decoded
                    elif content_type == 'text/html':
                        body_html = decoded
            except Exception as e:
                print(f"解析邮件正文失败: {e}")

        return body_text, body_html

    async def disconnect(self):
        """断开连接"""
        if self.client:
            try:
                await self.client.logout()
            except:
                pass
            self.client = None
