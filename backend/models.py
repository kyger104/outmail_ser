from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class Mailbox(Base):
    __tablename__ = "mailboxes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    imap_token = Column(Text, nullable=False)  # 加密存储
    imap_server = Column(String(100), default="outlook.office365.com")
    imap_port = Column(Integer, default=993)
    status = Column(String(20), default="active")  # active/inactive/error
    last_sync = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    emails = relationship("Email", back_populates="mailbox", cascade="all, delete-orphan")


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id"), nullable=False, index=True)
    message_id = Column(String(255), unique=True, index=True)
    subject = Column(Text)
    sender = Column(String(255), index=True)
    recipient = Column(String(255))
    date = Column(DateTime, index=True)
    body_text = Column(Text)
    body_html = Column(Text)
    is_read = Column(Boolean, default=False)
    has_attachments = Column(Boolean, default=False)
    raw_headers = Column(Text)
    received_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    mailbox = relationship("Mailbox", back_populates="emails")
    attachments = relationship("Attachment", back_populates="email", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False)
    filename = Column(String(255))
    content_type = Column(String(100))
    size = Column(Integer)
    file_path = Column(Text)

    # 关系
    email = relationship("Email", back_populates="attachments")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    rate_limit = Column(Integer, default=0)  # 0 = 无限制
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
