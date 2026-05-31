from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from database import get_db
from models import Mailbox
from utils.jwt_helper import JWTHelper
from scheduler import scheduler
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])


# Pydantic 模型
class MailboxImport(BaseModel):
    email: EmailStr
    imap_token: str


class MailboxBatchImport(BaseModel):
    mailboxes: List[MailboxImport]


class MailboxResponse(BaseModel):
    id: int
    email: str
    status: str
    last_sync: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/mailboxes/import")
async def import_mailboxes(data: MailboxBatchImport, db: Session = Depends(get_db)):
    """批量导入邮箱"""
    imported = []
    errors = []

    for mailbox_data in data.mailboxes:
        try:
            # 检查是否已存在
            existing = db.query(Mailbox).filter(Mailbox.email == mailbox_data.email).first()
            if existing:
                errors.append(f"{mailbox_data.email} 已存在")
                continue

            # 创建新邮箱
            mailbox = Mailbox(
                email=mailbox_data.email,
                imap_token=mailbox_data.imap_token,  # TODO: 需要加密
                status="active"
            )
            db.add(mailbox)
            db.flush()

            # 生成 JWT token
            jwt_token = JWTHelper.generate_mailbox_token(
                mailbox_id=mailbox.id,
                email=mailbox.email
            )
            mailbox.jwt_token = jwt_token
            db.commit()
            db.refresh(mailbox)

            # 启动同步任务
            await scheduler.start_sync_task(mailbox.id)

            imported.append(mailbox.email)
        except Exception as e:
            errors.append(f"{mailbox_data.email}: {str(e)}")
            db.rollback()

    return {
        "imported": imported,
        "errors": errors,
        "total": len(imported)
    }


@router.get("/mailboxes", response_model=List[MailboxResponse])
def get_mailboxes(
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取邮箱列表"""
    offset = (page - 1) * limit
    mailboxes = db.query(Mailbox).offset(offset).limit(limit).all()
    return mailboxes


@router.delete("/mailboxes/{mailbox_id}")
async def delete_mailbox(mailbox_id: int, db: Session = Depends(get_db)):
    """删除邮箱"""
    mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id).first()
    if not mailbox:
        raise HTTPException(status_code=404, detail="邮箱不存在")

    # 停止同步任务
    await scheduler.stop_sync_task(mailbox_id)

    # 删除邮箱（级联删除邮件）
    db.delete(mailbox)
    db.commit()

    return {"message": "邮箱已删除"}


@router.get("/mailboxes/links")
def get_all_mailbox_links(db: Session = Depends(get_db)):
    """获取所有邮箱的访问链接"""
    mailboxes = db.query(Mailbox).all()
    results = []
    for mailbox in mailboxes:
        if not mailbox.jwt_token:
            jwt_token = JWTHelper.generate_mailbox_token(
                mailbox_id=mailbox.id,
                email=mailbox.email
            )
            mailbox.jwt_token = jwt_token
        link = JWTHelper.generate_mailbox_url(mailbox.jwt_token)
        results.append({
            "id": mailbox.id,
            "email": mailbox.email,
            "link": link,
            "status": mailbox.status
        })
    db.commit()
    return {"items": results, "total": len(results)}


@router.get("/mailboxes/{id}/link")
def get_mailbox_link(id: int, db: Session = Depends(get_db)):
    """获取单个邮箱的访问链接"""
    mailbox = db.query(Mailbox).filter(Mailbox.id == id).first()
    if not mailbox:
        raise HTTPException(status_code=404, detail="邮箱不存在")
    if not mailbox.jwt_token:
        jwt_token = JWTHelper.generate_mailbox_token(
            mailbox_id=mailbox.id,
            email=mailbox.email
        )
        mailbox.jwt_token = jwt_token
        db.commit()
    link = JWTHelper.generate_mailbox_url(mailbox.jwt_token)
    return {
        "mailbox_id": mailbox.id,
        "email": mailbox.email,
        "jwt_token": mailbox.jwt_token,
        "link": link
    }


@router.get("/mailboxes/{mailbox_id}", response_model=MailboxResponse)
def get_mailbox(mailbox_id: int, db: Session = Depends(get_db)):
    """获取单个邮箱详情"""
    mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id).first()
    if not mailbox:
        raise HTTPException(status_code=404, detail="邮箱不存在")
    return mailbox
