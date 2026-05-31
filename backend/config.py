from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "sqlite:///./data/emails.db"

    # IMAP 配置
    imap_server: str = "outlook.office365.com"
    imap_port: int = 993
    sync_interval: int = 30  # 秒

    # 管理员认证
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # 加密密钥
    encryption_key: str = "your-encryption-key-32-bytes-long"
    secret_key: str = "your-secret-key-here"

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 7892

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
