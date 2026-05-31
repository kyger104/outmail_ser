"""
完整的项目测试脚本
测试所有关键功能是否正常工作
"""
import sys
from pathlib import Path

# 设置 UTF-8 输出
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("开始项目完整性测试")
print("=" * 60)

# 1. 测试配置加载
print("\n[1/8] 测试配置加载...")
try:
    from config import get_settings
    settings = get_settings()
    print(f"  [OK] 配置加载成功")
    print(f"    - 数据库: {settings.database_url}")
    print(f"    - 端口: {settings.port}")
    print(f"    - Secret Key: {'已设置' if settings.secret_key else '未设置'}")
except Exception as e:
    print(f"  [FAIL] 配置加载失败: {e}")
    sys.exit(1)

# 2. 测试数据库模型
print("\n[2/8] 测试数据库模型...")
try:
    from models import Mailbox, Email, APIKey
    print(f"  [OK] 数据库模型导入成功")
    print(f"    - Mailbox: {Mailbox.__tablename__}")
    print(f"    - Email: {Email.__tablename__}")
    print(f"    - APIKey: {APIKey.__tablename__}")
except Exception as e:
    print(f"  [FAIL] 数据库模型导入失败: {e}")
    sys.exit(1)

# 3. 测试数据库初始化
print("\n[3/8] 测试数据库初始化...")
try:
    from database import init_db, get_db
    init_db()
    print(f"  [OK] 数据库初始化成功")

    # 检查数据库文件
    db_path = Path("data/emails.db")
    if db_path.exists():
        print(f"    - 数据库文件: {db_path} ({db_path.stat().st_size} bytes)")
    else:
        print(f"    - 数据库文件将在首次运行时创建")
except Exception as e:
    print(f"  [FAIL] 数据库初始化失败: {e}")
    sys.exit(1)

# 4. 测试 JWT Helper
print("\n[4/8] 测试 JWT Helper...")
try:
    from utils.jwt_helper import JWTHelper

    # 生成测试 token
    test_token = JWTHelper.generate_mailbox_token(1, "test@example.com")
    print(f"  [OK] JWT token 生成成功")
    print(f"    - Token 长度: {len(test_token)}")

    # 验证 token
    payload = JWTHelper.verify_mailbox_token(test_token)
    if payload and payload.get("email") == "test@example.com":
        print(f"  [OK] JWT token 验证成功")
        print(f"    - Mailbox ID: {payload.get('mailbox_id')}")
        print(f"    - Email: {payload.get('email')}")
    else:
        print(f"  [FAIL] JWT token 验证失败")
        sys.exit(1)

    # 生成访问链接
    link = JWTHelper.generate_mailbox_url(test_token)
    print(f"  [OK] 访问链接生成成功")
    print(f"    - Link: {link[:50]}...")

except Exception as e:
    print(f"  [FAIL] JWT Helper 测试失败: {e}")
    sys.exit(1)

# 5. 测试路由导入
print("\n[5/8] 测试路由导入...")
try:
    from routers import admin, emails, inbox, api_keys, external_api_dual
    print(f"  [OK] 所有路由导入成功")
    print(f"    - admin: {admin.router.prefix}")
    print(f"    - emails: {emails.router.prefix}")
    print(f"    - inbox: {inbox.router.prefix}")
    print(f"    - api_keys: {api_keys.router.prefix}")
    print(f"    - external_api_dual: {external_api_dual.router.prefix}")
except Exception as e:
    print(f"  [FAIL] 路由导入失败: {e}")
    sys.exit(1)

# 6. 测试 FastAPI 应用创建
print("\n[6/8] 测试 FastAPI 应用创建...")
try:
    from main import app
    print(f"  [OK] FastAPI 应用创建成功")
    print(f"    - Title: {app.title}")
    print(f"    - Version: {app.version}")

    # 检查路由注册
    routes = [route.path for route in app.routes]
    api_routes = [r for r in routes if r.startswith('/api')]
    print(f"    - API 路由数量: {len(api_routes)}")

except Exception as e:
    print(f"  [FAIL] FastAPI 应用创建失败: {e}")
    sys.exit(1)

# 7. 测试前端文件
print("\n[7/8] 测试前端文件...")
try:
    frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
    frontend_src = Path(__file__).parent.parent / "frontend" / "src"

    if frontend_dist.exists() and (frontend_dist / "index.html").exists():
        print(f"  [OK] 前端已构建")
        print(f"    - Dist 目录: {frontend_dist}")
        print(f"    - index.html: 存在")

        assets_dir = frontend_dist / "assets"
        if assets_dir.exists():
            asset_files = list(assets_dir.glob("*"))
            print(f"    - Assets 文件数: {len(asset_files)}")
    else:
        print(f"  [WARN] 前端未构建（需要运行 npm run build）")
        print(f"    - Src 目录: {frontend_src} ({'存在' if frontend_src.exists() else '不存在'})")

except Exception as e:
    print(f"  [FAIL] 前端文件检查失败: {e}")

# 8. 测试依赖包
print("\n[8/8] 测试关键依赖包...")
try:
    import fastapi
    import sqlalchemy
    import jwt
    import uvicorn

    print(f"  [OK] 所有关键依赖已安装")
    print(f"    - FastAPI: {fastapi.__version__}")
    print(f"    - SQLAlchemy: {sqlalchemy.__version__}")
    print(f"    - PyJWT: {jwt.__version__}")
    print(f"    - Uvicorn: {uvicorn.__version__}")

except ImportError as e:
    print(f"  [FAIL] 依赖包缺失: {e}")
    print(f"    请运行: pip install -r requirements.txt")
    sys.exit(1)

print("\n" + "=" * 60)
print("[OK] 所有测试通过！项目可以正常运行")
print("=" * 60)
print("\n启动命令:")
print("  python main.py")
print("  或")
print("  uvicorn main:app --host 0.0.0.0 --port 7892")
print("\n访问地址:")
print("  - API 文档: http://localhost:7892/docs")
print("  - 管理后台: http://localhost:7892/admin")
print("  - 收件箱: http://localhost:7892/inbox")
print("=" * 60)
