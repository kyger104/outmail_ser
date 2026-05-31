"""
External API Router - Dual Mode (Graph API + IMAP)
Supports both Microsoft Graph API and IMAP methods
"""
from fastapi import APIRouter, Query, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging
from sqlalchemy.orm import Session

from services.token_manager import TokenManager
from services.microsoft_graph import MicrosoftGraphClient
from services.imap_service import IMAPService
from middleware.rate_limiter import check_rate_limit
from routers.api_keys import verify_api_key
from database import get_db

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
    request: Request,
    email: EmailStr = Query(..., description="邮箱地址 (如: xxx@outlook.com)"),
    clientId: str = Query(None, description="Azure AD 客户端 ID (Graph API 方式)"),
    refreshToken: str = Query(None, description="微软刷新令牌 (Graph API 方式)"),
    password: str = Query(None, description="邮箱密码或应用密码 (IMAP 方式)"),
    num: int = Query(1, ge=1, le=5, description="获取邮件数量 (默认: 1, 最大: 5)"),
    boxType: int = Query(1, ge=1, le=2, description="邮箱类型 (1: 收件箱, 2: 垃圾箱)"),
    api_key: str = Query(None, description="API Key (白名单用户)"),
    db: Session = Depends(get_db)
):
    """
    获取指定邮箱的最新邮件

    支持两种认证方式：
    1. Graph API: 提供 clientId + refreshToken
    2. IMAP: 提供 password

    速率限制：
    - 白名单用户（提供有效 api_key）：无限制
    - 普通用户：20次/分钟

    Args:
        email: 邮箱地址
        clientId: Azure AD 应用客户端 ID (Graph API)
        refreshToken: OAuth2 刷新令牌 (Graph API)
        password: 邮箱密码或应用密码 (IMAP)
        num: 获取邮件数量 (1-5)
        boxType: 邮箱类型 (1=收件箱, 2=垃圾箱)
        api_key: API Key (白名单用户)

    Returns:
        GetLastEmailsResponse with email list or error
    """
    try:
        # 验证 API Key
        db_api_key = None
        if api_key:
            db_api_key = verify_api_key(api_key, db)
            if not db_api_key:
                logger.warning(f"Invalid API key provided: {api_key[:10]}...")
                # 无效的 API Key，按普通用户处理

        # 速率限制检查
        rate_limit = db_api_key.rate_limit if db_api_key else None
        await check_rate_limit(request, api_key if db_api_key else None, rate_limit)

        logger.info(f"GetLastEmails request: email={email}, num={num}, boxType={boxType}, has_api_key={bool(db_api_key)}")

        # Determine authentication method
        if clientId and refreshToken:
            # Method 1: Microsoft Graph API
            logger.info("Using Microsoft Graph API method")
            return await _get_emails_via_graph_api(
                email=email,
                client_id=clientId,
                refresh_token=refreshToken,
                num=num,
                box_type=boxType
            )
        elif password:
            # Method 2: IMAP
            logger.info("Using IMAP method")
            return await _get_emails_via_imap(
                email=email,
                password=password,
                num=num,
                box_type=boxType
            )
        else:
            logger.error("No valid authentication credentials provided")
            return GetLastEmailsResponse(
                code=400,
                message="参数错误",
                data=None,
                error="Please provide either (clientId + refreshToken) for Graph API or (password) for IMAP"
            )

    except HTTPException as e:
        # 速率限制异常，直接抛出
        raise e
    except Exception as e:
        logger.error(f"Exception in GetLastEmails: {str(e)}", exc_info=True)
        return GetLastEmailsResponse(
            code=500,
            message="服务器错误",
            data=None,
            error=str(e)
        )


async def _get_emails_via_graph_api(
    email: str,
    client_id: str,
    refresh_token: str,
    num: int,
    box_type: int
) -> GetLastEmailsResponse:
    """Get emails using Microsoft Graph API"""
    try:
        # Step 1: Get access token
        access_token = await token_manager.get_access_token(
            client_id=client_id,
            refresh_token=refresh_token,
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
            box_type=box_type
        )

        # Step 3: Return result
        if emails:
            logger.info(f"Successfully retrieved {len(emails)} emails via Graph API")
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
        logger.error(f"Graph API error: {str(e)}")
        return GetLastEmailsResponse(
            code=500,
            message="Graph API 错误",
            data=None,
            error=str(e)
        )


async def _get_emails_via_imap(
    email: str,
    password: str,
    num: int,
    box_type: int
) -> GetLastEmailsResponse:
    """Get emails using IMAP protocol"""
    try:
        # Use IMAP service
        async with IMAPService(email, password) as imap_service:
            emails = await imap_service.get_last_emails(
                num=num,
                box_type=box_type
            )

            if emails:
                logger.info(f"Successfully retrieved {len(emails)} emails via IMAP")
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
        logger.error(f"IMAP error: {str(e)}")
        return GetLastEmailsResponse(
            code=500,
            message="IMAP 错误",
            data=None,
            error=f"IMAP authentication or connection failed: {str(e)}"
        )
