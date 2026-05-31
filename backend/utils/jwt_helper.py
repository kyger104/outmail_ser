import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from config import get_settings

settings = get_settings()


class JWTHelper:
    """JWT 令牌生成和验证工具类"""

    @staticmethod
    def generate_mailbox_token(mailbox_id: int, email: str) -> str:
        """
        为邮箱生成专属 JWT token

        Args:
            mailbox_id: 邮箱 ID
            email: 邮箱地址

        Returns:
            JWT token 字符串
        """
        payload = {
            "mailbox_id": mailbox_id,
            "email": email,
            "type": "mailbox_access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=365)  # 1年有效期
        }

        token = jwt.encode(
            payload,
            settings.secret_key,
            algorithm="HS256"
        )

        return token

    @staticmethod
    def verify_mailbox_token(token: str) -> Optional[Dict]:
        """
        验证邮箱 JWT token

        Args:
            token: JWT token 字符串

        Returns:
            解码后的 payload，验证失败返回 None
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"]
            )

            # 验证 token 类型
            if payload.get("type") != "mailbox_access":
                return None

            return payload

        except jwt.ExpiredSignatureError:
            # Token 已过期
            return None
        except jwt.InvalidTokenError:
            # Token 无效
            return None

    @staticmethod
    def generate_mailbox_url(token: str, base_url: str = "https://chace123.sbs") -> str:
        """
        生成邮箱访问链接

        Args:
            token: JWT token
            base_url: 基础 URL

        Returns:
            完整的访问链接
        """
        return f"{base_url}/?jwt={token}"
