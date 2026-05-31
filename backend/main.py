from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from scheduler import scheduler
from routers import admin, emails, external_api_dual, api_keys
from config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("初始化数据库...")
    init_db()
    print("启动邮件同步调度器...")
    await scheduler.start()

    yield

    # 关闭时
    print("停止邮件同步调度器...")
    await scheduler.stop()


# 创建 FastAPI 应用
app = FastAPI(
    title="轻量级 IMAP 邮件托管系统",
    description="支持 Hotmail/Outlook 邮箱的 IMAP 邮件托管",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(admin.router)
app.include_router(emails.router)
app.include_router(external_api_dual.router)
app.include_router(api_keys.router)


@app.get("/")
def root():
    return {
        "message": "轻量级 IMAP 邮件托管系统",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
