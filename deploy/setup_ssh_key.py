"""
自动设置 SSH Key 到服务器
"""
import paramiko
import sys

# 服务器配置
HOST = "118.194.253.6"
PORT = 22
USERNAME = "root"
PASSWORD = "CHANGE_ME_PASSWORD"

# SSH 公钥
PUBLIC_KEY = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDZQBctlEu4vqnbqOBX/Xa78xpVNo1Tv6j1ywEGJ6tvC0KnNCOIz4xofgYIMhxS9Jur4eRn2dNL0nxBI4GcG/d0JiMvqsJnNGSr9IN4mGZUdO4JwdRG7MNK/OtEq/LpTy7H/+fInvm4l2cE55fG1Arx8RRSbVbXWU+whxAqG3qt8TFK4plXXBQKV2u+6+sG3hmQMSfvFOcOcyrTwzg7MbjD4yLFm+Ob2aD0SVsC+I1dTeyCUnXMh4LnHTIYJDTqmQ/6mXu2n6X7Evmz2EB0ZEt34nlQdBKb38kMR4D3zedji45kJMbBgIL+zAIOA7r2cOhvKT7GpnnP+ds3qNXVC25nuyg0Mx1TFDtJQvyylkm0e+hxKugeACOfwd20I06JnAu0ObWFSWo2EnZNklMz9kt8YEC+f8IJV7VLhcq4kbhGYAMGtML1Pvx4xvHIQhV9J7l4dHVeF5YUkHjSxB4xa+369EVvJTvgy1EsQc9iW6X/UJESshPSJYcXc0D1ZqGYWbyymWrzzd79z3nwxA0QNeS40x/QU9ndV0tT85L6VdmkR/PzshcexY47VVGT1OTeT4AhtKcaQYTB8glU/H4+PUL5n0Ksp7YhzFPDUb7aLWjy0IK/XboNm7vA5Igqc/DjWz501GcRNOUPdtbPcXEgI16yenSon/MVYiwTKR5fQPGzaw== admin@DESKTOP-LMTQJ4U"""

# 设置命令
SETUP_COMMANDS = f"""
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '{PUBLIC_KEY}' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "SSH key 已添加到 authorized_keys"
"""

def setup_ssh_key():
    """设置 SSH key"""
    print("=" * 60)
    print("开始设置 SSH Key")
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
        print("[OK] SSH 连接成功\n")

        # 执行设置命令
        print("正在设置 SSH key...\n")
        stdin, stdout, stderr = client.exec_command(SETUP_COMMANDS)

        # 输出结果
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        if output:
            print(output)

        if error and "already exists" not in error.lower():
            print(f"警告: {error}")

        # 验证设置
        print("\n验证 SSH key 设置...")
        stdin, stdout, stderr = client.exec_command("cat ~/.ssh/authorized_keys | grep 'admin@DESKTOP-LMTQJ4U'")
        result = stdout.read().decode('utf-8')

        if result:
            print("[OK] SSH key 已成功添加到服务器")
            print("\n" + "=" * 60)
            print("[OK] 设置完成！现在可以免密码登录了")
            print("=" * 60)
            print("\n测试免密码登录:")
            print("  ssh root@118.194.253.6")
            print("\n现在可以运行自动化部署:")
            print("  python deploy/auto_deploy_ssh.py")
        else:
            print("[FAIL] SSH key 添加失败")
            sys.exit(1)

        # 关闭连接
        client.close()

    except paramiko.AuthenticationException:
        print("[错误] 认证失败，请检查用户名和密码")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"[错误] SSH 连接失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[错误] 设置失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        setup_ssh_key()
    except KeyboardInterrupt:
        print("\n\n设置已取消")
        sys.exit(1)
