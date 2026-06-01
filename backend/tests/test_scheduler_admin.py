import asyncio
import sys
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from models import Base, Mailbox
from database import ensure_sqlite_schema
from routers import admin
from scheduler import EmailScheduler


class SchedulerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self):
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task() and not task.done():
                task.cancel()

    async def test_start_sync_task_uses_single_background_task(self):
        scheduler = EmailScheduler()
        scheduler.running = True

        await scheduler.start_sync_task(1)
        await scheduler.start_sync_task(2)

        self.assertLessEqual(len(scheduler.tasks), 1)
        await scheduler.stop()


class AdminImportTests(unittest.IsolatedAsyncioTestCase):
    def test_sqlite_migration_adds_jwt_token_to_existing_mailboxes_table(self):
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as connection:
            connection.execute(text("""
                CREATE TABLE mailboxes (
                    id INTEGER PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    imap_token TEXT NOT NULL,
                    imap_server VARCHAR(100),
                    imap_port INTEGER,
                    status VARCHAR(20),
                    last_sync DATETIME,
                    created_at DATETIME
                )
            """))

        ensure_sqlite_schema(engine)

        columns = {column["name"] for column in inspect(engine).get_columns("mailboxes")}
        self.assertIn("jwt_token", columns)

    async def test_import_returns_compatible_and_frontend_friendly_fields(self):
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        class FakeScheduler:
            def __init__(self):
                self.submitted = []

            async def start_sync_task(self, mailbox_id):
                self.submitted.append(mailbox_id)

        original_scheduler = admin.scheduler
        admin.scheduler = FakeScheduler()
        try:
            payload = admin.MailboxBatchImport(
                mailboxes=[
                    admin.MailboxImport(email="one@example.com", imap_token="token"),
                    admin.MailboxImport(email="one@example.com", imap_token="token"),
                ]
            )

            result = await admin.import_mailboxes(payload, db)

            self.assertEqual(result["imported"], ["one@example.com"])
            self.assertEqual(result["total"], 1)
            self.assertEqual(result["submitted"], 1)
            self.assertEqual(result["skipped"], 1)
            self.assertEqual(len(result["items"]), 1)
            self.assertIn("link", result["items"][0])
            self.assertEqual(db.query(Mailbox).count(), 1)
        finally:
            admin.scheduler = original_scheduler
            db.close()


if __name__ == "__main__":
    unittest.main()
