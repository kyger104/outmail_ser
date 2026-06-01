"""
自动化部署脚本 - 使用 paramiko 库
"""
import paramiko
import time
import sys

# 服务器配置
HOST = "118.194.253.6"
PORT = 22
USERNAME = "root"
PASSWORD = "CHANGE_ME_PASSWORD"

# 部署命令
DEPLOY_COMMANDS = """
cd /opt/imap && \
git pull origin main && \
echo "✓ 代码已更新" && \
cp data/emails.db data/emails.db.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "✓ 数据库备份（首次运行可能无文件）" && \
cd backend && \
source .venv/bin/activate && \
pip install -r requirements.txt -q && \
echo "✓ 依赖已安装" && \
systemctl restart imap-backend && \
echo "✓ 服务已重启" && \
sleep 3 && \
systemctl is-active imap-backend && \
echo "" && \
echo "========================================" && \
echo "测试 API:" && \
curl -s http://127.0.0.1:7892/health && \
echo "" && \
echo "========================================" && \
echo "✅ 部署完成！" && \
echo "========================================" && \
echo "" && \
echo "访问地址：" && \
echo "- 管理后台：https://chace123.sbs/admin" && \
echo "- API 文档：https://chace123.sbs/docs" && \
echo "- 收件箱：https://chace123.sbs/inbox"
"""

def deploy():
    """执行部署"""
    print("=" * 60)
    print("开始自动化部署到服务器")
    print("=" * 60)
    print(f"\n连接到服务器: {HOST}...")

    try:
        # 创建 SSH 客户端
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接服务器
        client.connect(
            hostname=HOST,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
            timeout=10
        )
        print("✓ SSH 连接成功\n")

        # 执行部署命令
        print("执行部署命令...\n")
        stdin, stdout, stderr = client.exec_command(DEPLOY_COMMANDS, get_pty=True)

        # 实时输出结果
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line.rstrip())

        # 检查错误
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            print(f"\n[错误] 部署失败，退出码: {exit_status}")
            stderr_output = stderr.read().decode('utf-8')
            if stderr_output:
                print(f"错误信息:\n{stderr_output}")
            sys.exit(1)

        print("\n" + "=" * 60)
        print("✅ 部署成功完成！")
        print("=" * 60)

        # 关闭连接
        client.close()

    except paramiko.AuthenticationException:
        print("[错误] 认证失败，请检查用户名和密码")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"[错误] SSH 连接失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[错误] 部署失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        deploy()
    except KeyboardInterrupt:
        print("\n\n部署已取消")
        sys.exit(1)
