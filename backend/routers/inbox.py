from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Mailbox, Email
from utils.jwt_helper import JWTHelper

router = APIRouter(prefix="/api/inbox", tags=["inbox"])


@router.get("/verify")
def verify_jwt(jwt: str, db: Session = Depends(get_db)):
    payload = JWTHelper.verify_mailbox_token(jwt)
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的访问链接")
    mailbox_id = payload.get("mailbox_id")
    mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id).first()
    if not mailbox:
        raise HTTPException(status_code=404, detail="邮箱不存在")
    return {
        "mailbox_id": mailbox.id,
        "email": mailbox.email,
        "status": mailbox.status
    }


@router.get("/emails")
def get_emails(
    jwt: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    payload = JWTHelper.verify_mailbox_token(jwt)
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的访问链接")
    mailbox_id = payload.get("mailbox_id")
    query = db.query(Email).filter(Email.mailbox_id == mailbox_id)
    total = query.count()
    emails = query.order_by(Email.date.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    return {
        "items": [
            {
                "id": email.id,
                "subject": email.subject,
                "sender": email.sender,
                "date": email.date.isoformat() if email.date else None,
                "is_read": email.is_read,
                "has_attachments": email.has_attachments,
                "body_preview": email.body_text[:200] if email.body_text else ""
            }
            for email in emails
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/emails/{email_id}")
def get_email_detail(
    email_id: int,
    jwt: str,
    db: Session = Depends(get_db)
):
    payload = JWTHelper.verify_mailbox_token(jwt)
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的访问链接")
    mailbox_id = payload.get("mailbox_id")
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.mailbox_id == mailbox_id
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="邮件不存在")
    if not email.is_read:
        email.is_read = True
        db.commit()
    return {
        "id": email.id,
        "subject": email.subject,
        "sender": email.sender,
        "recipient": email.recipient,
        "date": email.date.isoformat() if email.date else None,
        "body_text": email.body_text,
        "body_html": email.body_html,
        "is_read": email.is_read,
        "has_attachments": email.has_attachments
    }
