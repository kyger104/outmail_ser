from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from pydantic import BaseModel
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from database import get_db
from models import Email, Mailbox
from scheduler import scheduler

router = APIRouter(prefix="/api/emails", tags=["emails"])


# Pydantic 模型
class EmailListResponse(BaseModel):
    id: int
    subject: str
    sender: str
    date: datetime
    is_read: bool
    has_attachments: bool

    class Config:
        from_attributes = True


class EmailDetailResponse(BaseModel):
    id: int
    subject: str
    sender: str
    recipient: str
    date: datetime
    body_text: str
    body_html: str
    is_read: bool
    has_attachments: bool
    received_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[EmailListResponse])
def get_emails(
    mailbox_id: int = Query(..., description="邮箱 ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取邮件列表"""
    # 验证邮箱是否存在
    mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id).first()
    if not mailbox:
        raise HTTPException(status_code=404, detail="邮箱不存在")

    # 分页查询邮件
    offset = (page - 1) * limit
    emails = (
        db.query(Email)
        .filter(Email.mailbox_id == mailbox_id)
        .order_by(desc(Email.date))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return emails


@router.get("/{email_id}", response_model=EmailDetailResponse)
def get_email_detail(email_id: int, db: Session = Depends(get_db)):
    """获取邮件详情"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="邮件不存在")

    return email


@router.put("/{email_id}/read")
def mark_as_read(email_id: int, db: Session = Depends(get_db)):
    """标记邮件为已读"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="邮件不存在")

    email.is_read = True
    db.commit()

    return {"message": "已标记为已读"}


@router.post("/refresh")
async def refresh_emails(
    mailbox_id: int = Query(..., description="邮箱 ID"),
    db: Session = Depends(get_db)
):
    """手动刷新邮件"""
    # 验证邮箱是否存在
    mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id).first()
    if not mailbox:
        raise HTTPException(status_code=404, detail="邮箱不存在")

    # 立即同步
    await scheduler.sync_mailbox(mailbox_id)

    return {"message": "刷新完成"}


@router.get("/stats/{mailbox_id}")
def get_email_stats(mailbox_id: int, db: Session = Depends(get_db)):
    """获取邮件统计信息"""
    # 验证邮箱是否存在
    mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id).first()
    if not mailbox:
        raise HTTPException(status_code=404, detail="邮箱不存在")

    total = db.query(Email).filter(Email.mailbox_id == mailbox_id).count()
    unread = db.query(Email).filter(
        Email.mailbox_id == mailbox_id,
        Email.is_read == False
    ).count()

    return {
        "total": total,
        "unread": unread,
        "read": total - unread
    }
