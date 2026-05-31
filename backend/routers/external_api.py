"""
External API Router
Provides GetLastEmails endpoint for external systems
"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging

from services.token_manager import TokenManager
from services.microsoft_graph import MicrosoftGraphClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["external"])
token_manager = TokenManager()


class EmailItem(BaseModel):
    """Email item model"""
    Date: str
    From: str
    To: str
    Subject: str
    Body: str
    BodyPreview: str
    HasAttachments: bool
    IsRead: bool


class GetLastEmailsResponse(BaseModel):
    """Response model for GetLastEmails endpoint"""
    code: int
    message: str
    data: Optional[List[EmailItem]] = None
    error: Optional[str] = None


@router.get("/GetLastEmails", response_model=GetLastEmailsResponse)
async def get_last_emails(
    email: EmailStr = Query(..., description="邮箱地址 (如: xxx@outlook.com)"),
    clientId: str = Query(..., description="Azure AD 客户端 ID"),
    refreshToken: str = Query(..., description="微软刷新令牌"),
    num: int = Query(1, ge=1, le=5, description="获取邮件数量 (默认: 1, 最大: 5)"),
    boxType: int = Query(1, ge=1, le=2, description="邮箱类型 (1: 收件箱, 2: 垃圾箱)")
):
    """
    获取指定邮箱的最新邮件

    Args:
        email: 邮箱地址
        clientId: Azure AD 应用客户端 ID
        refreshToken: OAuth2 刷新令牌
        num: 获取邮件数量 (1-5)
        boxType: 邮箱类型 (1=收件箱, 2=垃圾箱)

    Returns:
        GetLastEmailsResponse with email list or error
    """
    try:
        logger.info(f"GetLastEmails request: email={email}, num={num}, boxType={boxType}")

        # Step 1: Get access token
        access_token = await token_manager.get_access_token(
            client_id=clientId,
            refresh_token=refreshToken,
            email=email
        )

        if not access_token:
            logger.error(f"Failed to obtain access token for {email}")
            return GetLastEmailsResponse(
                code=401,
                message="认证失败",
                data=None,
                error="Failed to obtain access token. Please check your clientId and refreshToken."
            )

        # Step 2: Call Graph API
        graph_client = MicrosoftGraphClient(access_token)
        emails = await graph_client.get_last_emails(
            email=email,
            num=num,
            box_type=boxType
        )

        # Step 3: Return result
        if emails:
            logger.info(f"Successfully retrieved {len(emails)} emails for {email}")
            return GetLastEmailsResponse(
                code=200,
                message="获取成功",
                data=emails
            )
        else:
            logger.warning(f"No emails found for {email}")
            return GetLastEmailsResponse(
                code=200,
                message="获取成功",
                data=[]
            )

    except Exception as e:
        logger.error(f"Exception in GetLastEmails: {str(e)}", exc_info=True)
        return GetLastEmailsResponse(
            code=500,
            message="服务器错误",
            data=None,
            error=str(e)
        )
