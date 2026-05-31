"""
API Key 管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import secrets

from database import get_db
from models import APIKey
from config import get_settings

router = APIRouter(prefix="/api/admin", tags=["API Key 管理"])
security = HTTPBasic()
settings = get_settings()


# Pydantic 模型
class APIKeyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rate_limit: int = 0  # 0 = 无限制


class APIKeyUpdate(BaseModel):
    rate_limit: Optional[int] = None
    is_active: Optional[bool] = None


class APIKeyResponse(BaseModel):
    id: int
    api_key: str
    name: str
    description: Optional[str]
    rate_limit: int
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]
    usage_count: int

    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    items: List[APIKeyResponse]
    total: int


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """验证管理员身份"""
    correct_username = secrets.compare_digest(
        credentials.username, settings.admin_username
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.admin_password
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def generate_api_key() -> str:
    """生成 API Key"""
    return f"sk_{secrets.token_urlsafe(32)}"


@router.post("/api-keys", response_model=APIKeyResponse)
def create_api_key(
    api_key_data: APIKeyCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """创建 API Key"""
    # 生成唯一的 API Key
    api_key = generate_api_key()

    # 创建数据库记录
    db_api_key = APIKey(
        api_key=api_key,
        name=api_key_data.name,
        description=api_key_data.description,
        rate_limit=api_key_data.rate_limit,
        is_active=True
    )

    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)

    return db_api_key


@router.get("/api-keys", response_model=APIKeyListResponse)
def list_api_keys(
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """获取 API Key 列表"""
    api_keys = db.query(APIKey).order_by(APIKey.created_at.desc()).all()

    return {
        "items": api_keys,
        "total": len(api_keys)
    }


@router.get("/api-keys/{api_key_id}", response_model=APIKeyResponse)
def get_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """获取单个 API Key"""
    api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key 不存在"
        )

    return api_key


@router.put("/api-keys/{api_key_id}", response_model=APIKeyResponse)
def update_api_key(
    api_key_id: int,
    api_key_data: APIKeyUpdate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """更新 API Key"""
    api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key 不存在"
        )

    # 更新字段
    if api_key_data.rate_limit is not None:
        api_key.rate_limit = api_key_data.rate_limit

    if api_key_data.is_active is not None:
        api_key.is_active = api_key_data.is_active

    db.commit()
    db.refresh(api_key)

    return api_key


@router.delete("/api-keys/{api_key_id}")
def delete_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin)
):
    """删除 API Key"""
    api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key 不存在"
        )

    db.delete(api_key)
    db.commit()

    return {"message": "API Key 已删除"}


def verify_api_key(api_key: str, db: Session) -> Optional[APIKey]:
    """
    验证 API Key

    Returns:
        APIKey 对象或 None
    """
    if not api_key:
        return None

    db_api_key = db.query(APIKey).filter(
        APIKey.api_key == api_key,
        APIKey.is_active == True
    ).first()

    if db_api_key:
        # 更新使用统计
        db_api_key.last_used = datetime.utcnow()
        db_api_key.usage_count += 1
        db.commit()

    return db_api_key
