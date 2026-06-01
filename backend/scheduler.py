import asyncio
from datetime import datetime
from models import Mailbox, Email
from imap_client import IMAPClient
from database import SessionLocal
from config import get_settings
from typing import Dict, Set

settings = get_settings()


class EmailScheduler:
    def __init__(self):
        self.tasks: Dict[int, asyncio.Task] = {}
        self.pending_mailboxes: Set[int] = set()
        self._loop_task: asyncio.Task | None = None
        self._wake_event = asyncio.Event()
        self.running = False

    async def start(self):
        """启动调度器"""
        if self.running:
            return

        self.running = True
        if not settings.enable_background_sync:
            print("邮件后台同步已禁用")
            return

        self._ensure_loop_task()
        print("邮件同步调度器已启动")

    async def stop(self):
        """停止调度器"""
        self.running = False
        for task in list(self.tasks.values()):
            task.cancel()
        self.tasks.clear()
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
            self._loop_task = None
        self.pending_mailboxes.clear()
        self._wake_event.set()
        print("邮件同步调度器已停止")

    async def start_sync_task(self, mailbox_id: int):
        """提交邮箱同步请求，后台只保留单个调度循环。"""
        self.pending_mailboxes.add(mailbox_id)
        self._wake_event.set()
        if not self.running or not settings.enable_background_sync:
            return

        self._ensure_loop_task()
        print(f"已提交邮箱 {mailbox_id} 的同步任务")

    async def stop_sync_task(self, mailbox_id: int):
        """取消邮箱的待同步请求。"""
        self.pending_mailboxes.discard(mailbox_id)
        print(f"已取消邮箱 {mailbox_id} 的待同步任务")

    def _ensure_loop_task(self):
        if not self._loop_task or self._loop_task.done():
            self._loop_task = asyncio.create_task(self._sync_loop())
            self.tasks = {0: self._loop_task}

    async def _sync_loop(self):
        """单调度循环，按批次和有限并发同步活跃邮箱。"""
        while self.running:
            try:
                self._wake_event.clear()
                mailbox_ids = self._get_next_mailbox_ids()
                if mailbox_ids:
                    await self._sync_batch(mailbox_ids)
                try:
                    await asyncio.wait_for(self._wake_event.wait(), timeout=max(settings.sync_interval, 1))
                except asyncio.TimeoutError:
                    pass
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"邮件同步调度循环出错: {e}")
                await asyncio.sleep(60)  # 出错后等待 60 秒

    def _get_next_mailbox_ids(self) -> list[int]:
        db = SessionLocal()
        try:
            batch_size = max(settings.sync_batch_size, 1)
            query = db.query(Mailbox.id).filter(Mailbox.status == "active")

            if self.pending_mailboxes:
                requested_ids = list(self.pending_mailboxes)
                self.pending_mailboxes.clear()
                requested = [
                    row[0]
                    for row in query.filter(Mailbox.id.in_(requested_ids))
                    .limit(batch_size)
                    .all()
                ]
                if requested:
                    return requested

            return [row[0] for row in query.order_by(Mailbox.last_sync.asc()).limit(batch_size).all()]
        finally:
            db.close()

    async def _sync_batch(self, mailbox_ids: list[int]):
        semaphore = asyncio.Semaphore(max(settings.sync_concurrency, 1))

        async def run_one(mailbox_id: int):
            async with semaphore:
                await self.sync_mailbox(mailbox_id)

        await asyncio.gather(*(run_one(mailbox_id) for mailbox_id in mailbox_ids))

    async def sync_mailbox(self, mailbox_id: int, force: bool = False):
        """同步单个邮箱"""
        db = SessionLocal()
        try:
            # 获取邮箱信息
            mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id).first()
            if not mailbox or (mailbox.status != "active" and not force):
                return {"mailbox_id": mailbox_id, "status": "skipped", "new_count": 0}

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
                return {"mailbox_id": mailbox_id, "status": "error", "new_count": 0}

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
            mailbox.status = "active"
            db.commit()

            await client.disconnect()

            if new_count > 0:
                print(f"邮箱 {mailbox.email} 同步完成，新增 {new_count} 封邮件")

            return {"mailbox_id": mailbox_id, "status": "ok", "new_count": new_count}

        except Exception as e:
            print(f"同步邮箱 {mailbox_id} 失败: {e}")
            db.rollback()
            return {"mailbox_id": mailbox_id, "status": "error", "new_count": 0, "error": str(e)}
        finally:
            db.close()


# 全局调度器实例
scheduler = EmailScheduler()
