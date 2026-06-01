"""
交互式 SSH 部署脚本
"""
import paramiko
import time
import sys

HOST = "118.194.253.6"
PORT = 22
USERNAME = "root"
PASSWORD = "CHANGE_ME_PASSWORD"

def execute_command(client, command, wait_time=2):
    """执行命令并返回输出"""
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    time.sleep(wait_time)

    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')

    return output, error

def main():
    print("=" * 60)
    print("开始诊断和修复")
    print("=" * 60)

    try:
        # 创建 SSH 客户端
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"\n[1/10] 连接到服务器 {HOST}...")
        client.connect(
            hostname=HOST,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
            timeout=15,
            look_for_keys=False,
            allow_agent=False
        )
        print("✓ SSH 连接成功\n")

        # 检查项目目录
        print("[2/10] 检查项目目录...")
        output, _ = execute_command(client, "ls -la /opt/mailser/")
        print(output)

        # 检查配置文件
        print("\n[3/10] 检查数据库配置...")
        output, _ = execute_command(client, "cat /opt/mailser/backend/config.py | grep database")
        print(output)

        # 检查当前数据库文件
        print("\n[4/10] 检查数据库文件...")
        output, _ = execute_command(client, "ls -la /opt/mailser/data/ 2>&1 || echo 'data目录不存在'")
        print(output)

        # 创建 data 目录
        print("\n[5/10] 确保 data 目录存在...")
        output, _ = execute_command(client, "mkdir -p /opt/mailser/data && echo '✓ data 目录已创建'")
        print(output)

        # 删除旧数据库
        print("\n[6/10] 备份并删除旧数据库...")
        output, _ = execute_command(client, """
cd /opt/mailser
if [ -f data/emails.db ]; then
    mv data/emails.db data/emails.db.backup.$(date +%Y%m%d_%H%M%S)
    echo '✓ 旧数据库已备份'
else
    echo '✓ 无旧数据库文件'
fi
""")
        print(output)

        # 重新初始化数据库
        print("\n[7/10] 重新初始化数据库...")
        output, _ = execute_command(client, """
cd /opt/mailser/backend
source .venv/bin/activate
python -c "from database import init_db; init_db(); print('✓ 数据库初始化成功')"
""", wait_time=5)
        print(output)

        # 验证数据库文件
        print("\n[8/10] 验证数据库文件...")
        output, _ = execute_command(client, "ls -lh /opt/mailser/data/emails.db")
        print(output)

        # 重启服务
        print("\n[9/10] 重启服务...")
        output, _ = execute_command(client, "systemctl restart imap-backend && echo '✓ 服务已重启'")
        print(output)
        time.sleep(3)

        # 检查服务状态
        print("\n[10/10] 检查服务状态...")
        output, _ = execute_command(client, "systemctl status imap-backend --no-pager -l", wait_time=2)
        print(output)

        # 测试 API
        print("\n" + "=" * 60)
        print("测试 API...")
        print("=" * 60)
        output, _ = execute_command(client, "curl -s http://127.0.0.1:7892/health")
        print(output)

        if '"status":"ok"' in output or '"status": "ok"' in output:
            print("\n" + "=" * 60)
            print("✅ 部署成功！")
            print("=" * 60)
            print("\n访问地址：")
            print("- 管理后台：https://chace123.sbs/admin")
            print("- API 文档：https://chace123.sbs/docs")
            print("- 收件箱：https://chace123.sbs/inbox")
        else:
            print("\n⚠ API 测试失败，查看日志...")
            output, _ = execute_command(client, "journalctl -u imap-backend -n 30 --no-pager")
            print(output)

        client.close()

    except paramiko.AuthenticationException:
        print("\n❌ SSH 认证失败")
        print("可能的原因：")
        print("1. 密码错误")
        print("2. 服务器禁用了密码认证")
        print("3. 需要使用 SSH key")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"\n❌ SSH 连接失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
