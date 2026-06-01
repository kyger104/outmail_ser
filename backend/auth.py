import secrets
from base64 import b64decode
from binascii import Error as BinasciiError

from fastapi import Header, HTTPException, status

from config import get_settings


def _parse_basic_authorization(authorization: str | None) -> tuple[str, str] | None:
    if not authorization:
        return None
    scheme, _, encoded = authorization.partition(" ")
    if scheme.lower() != "basic" or not encoded:
        return None
    try:
        decoded = b64decode(encoded, validate=True).decode("utf-8")
    except (BinasciiError, UnicodeDecodeError):
        return None
    username, separator, password = decoded.partition(":")
    if not separator:
        return None
    return username, password


def verify_admin(authorization: str | None = Header(default=None)) -> str:
    credentials = _parse_basic_authorization(authorization)
    settings = get_settings()
    username = credentials[0] if credentials else ""
    password = credentials[1] if credentials else ""
    correct_username = secrets.compare_digest(
        username, settings.admin_username
    )
    correct_password = secrets.compare_digest(
        password, settings.admin_password
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    return username
