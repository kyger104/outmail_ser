import paramiko
import sys
import time

HOST = "118.194.253.6"
USER = "root"
PASSWORD = "Aa121314"

commands = [
    ("拉取最新代码", "cd /opt/imap && git pull origin main"),
    ("备份数据库", "cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup.$(date +%Y%m%d_%H%M%S)"),
    ("更新数据库结构", 'sqlite3 /opt/imap/data/emails.db "ALTER TABLE mailboxes ADD COLUMN jwt_token VARCHAR(500);" 2>&1; sqlite3 /opt/imap/data/emails.db "CREATE INDEX IF NOT EXISTS idx_mailboxes_jwt_token ON mailboxes(jwt_token);" 2>&1'),
    ("安装 pyjwt 依赖", "cd /opt/imap/backend && source .venv/bin/activate && pip install pyjwt==2.9.0 2>&1 | tail -3"),
    ("重启后端服务", "systemctl restart imap-backend"),
    ("等待服务启动", "sleep 3"),
    ("检查服务状态", "systemctl status imap-backend --no-pager 2>&1 | head -10"),
    ("健康检查", "curl -s http://127.0.0.1:7892/health"),
    ("测试 inbox 路由", "curl -s -w '\\nHTTP %{http_code}' http://127.0.0.1:7892/api/inbox/verify?jwt=test"),
]

print("=" * 50)
print("开始部署到服务器", HOST)
print("=" * 50)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("\n✓ 已连接到服务器\n")

    for name, cmd in commands:
        print(f"[{name}]")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if out:
            print(out)
        if err and "ERROR" in err.upper():
            print(f"⚠ {err}")
        print()

    print("=" * 50)
    print("部署完成!")
    print("=" * 50)
    print("\n访问地址:")
    print("  管理后台: https://chace123.sbs/admin")
    print("  API 文档: https://chace123.sbs/docs")

except Exception as e:
    print(f"\n✗ 部署失败: {e}")
    sys.exit(1)
finally:
    client.close()
