import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from models import Mailbox, Email
from imap_client import IMAPClient
from database import SessionLocal
from config import get_settings
from typing import Dict

settings = get_settings()


class EmailScheduler:
    def __init__(self):
        self.tasks: Dict[int, asyncio.Task] = {}
        self.running = False

    async def start(self):
        """启动调度器"""
        self.running = True
        print("邮件同步调度器已启动")

        # 获取所有活跃邮箱
        db = SessionLocal()
        try:
            mailboxes = db.query(Mailbox).filter(Mailbox.status == "active").all()
            for mailbox in mailboxes:
                await self.start_sync_task(mailbox.id)
        finally:
            db.close()

    async def stop(self):
        """停止调度器"""
        self.running = False
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()
        print("邮件同步调度器已停止")

    async def start_sync_task(self, mailbox_id: int):
        """为单个邮箱启动同步任务"""
        if mailbox_id in self.tasks:
            return

        task = asyncio.create_task(self._sync_loop(mailbox_id))
        self.tasks[mailbox_id] = task
        print(f"已启动邮箱 {mailbox_id} 的同步任务")

    async def stop_sync_task(self, mailbox_id: int):
        """停止单个邮箱的同步任务"""
        if mailbox_id in self.tasks:
            self.tasks[mailbox_id].cancel()
            del self.tasks[mailbox_id]
            print(f"已停止邮箱 {mailbox_id} 的同步任务")

    async def _sync_loop(self, mailbox_id: int):
        """邮箱同步循环"""
        while self.running:
            try:
                await self.sync_mailbox(mailbox_id)
                await asyncio.sleep(settings.sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"同步邮箱 {mailbox_id} 时出错: {e}")
                await asyncio.sleep(60)  # 出错后等待 60 秒

    async def sync_mailbox(self, mailbox_id: int):
        """同步单个邮箱"""
        db = SessionLocal()
        try:
            # 获取邮箱信息
            mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id).first()
            if not mailbox or mailbox.status != "active":
                return

            print(f"开始同步邮箱: {mailbox.email}")

            # 连接 IMAP
            client = IMAPClient(
                email_address=mailbox.email,
                token=mailbox.imap_token,  # TODO: 需要解密
                server=mailbox.imap_server,
                port=mailbox.imap_port
            )

            if not await client.connect():
                mailbox.status = "error"
                db.commit()
                return

            # 获取新邮件
            emails = await client.fetch_new_emails(limit=50)

            # 保存到数据库
            new_count = 0
            for email_data in emails:
                # 检查是否已存在
                existing = db.query(Email).filter(
                    Email.message_id == email_data['message_id']
                ).first()

                if not existing:
                    new_email = Email(
                        mailbox_id=mailbox.id,
                        message_id=email_data['message_id'],
                        subject=email_data['subject'],
                        sender=email_data['sender'],
                        recipient=email_data['recipient'],
                        date=email_data['date'],
                        body_text=email_data['body_text'],
                        body_html=email_data['body_html'],
                        has_attachments=email_data['has_attachments'],
                        raw_headers=email_data['raw_headers']
                    )
                    db.add(new_email)
                    new_count += 1

            # 更新同步时间
            mailbox.last_sync = datetime.utcnow()
            db.commit()

            await client.disconnect()

            if new_count > 0:
                print(f"邮箱 {mailbox.email} 同步完成，新增 {new_count} 封邮件")

        except Exception as e:
            print(f"同步邮箱 {mailbox_id} 失败: {e}")
            db.rollback()
        finally:
            db.close()


# 全局调度器实例
scheduler = EmailScheduler()
