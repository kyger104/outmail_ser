from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from models import Base
from config import get_settings

settings = get_settings()

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_schema(engine)


def ensure_sqlite_schema(db_engine=engine):
    """补齐旧 SQLite 数据库缺失的轻量字段。"""
    if db_engine.dialect.name != "sqlite":
        return

    inspector = inspect(db_engine)
    if "mailboxes" not in inspector.get_table_names():
        return

    mailbox_columns = {column["name"] for column in inspector.get_columns("mailboxes")}
    with db_engine.begin() as connection:
        if "jwt_token" not in mailbox_columns:
            connection.execute(text("ALTER TABLE mailboxes ADD COLUMN jwt_token VARCHAR(500)"))
        connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_mailboxes_jwt_token ON mailboxes (jwt_token)"))


def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
