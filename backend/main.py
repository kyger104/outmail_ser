from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
from database import init_db
from scheduler import scheduler
from routers import admin, emails, external_api_dual, api_keys, inbox
from config import get_settings

settings = get_settings()

# 前端静态文件目录
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


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
app.include_router(inbox.router)

# 挂载前端静态文件
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/")
def root():
    """根路径返回前端页面"""
    if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return {
        "message": "轻量级 IMAP 邮件托管系统",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/admin")
def admin_page():
    """管理后台页面"""
    if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return {"message": "请先构建前端"}


@app.get("/inbox")
def inbox_page():
    """收件箱页面"""
    if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return {"message": "请先构建前端"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/{spa_path:path}")
def spa_fallback(spa_path: str):
    """前端 SPA 路由兜底。API 和静态资源路径由上面的路由优先处理。"""
    if spa_path.startswith(("api/", "assets/")):
        return {"detail": "Not Found"}
    if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return {"message": "请先构建前端"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False
    )
