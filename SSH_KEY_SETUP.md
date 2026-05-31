# 🔑 手动设置 SSH Key 免密登录

## 方法一：使用 ssh-copy-id（推荐，最简单）

### Windows 用户（PowerShell）

```powershell
# 1. 复制公钥到服务器
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh root@118.194.253.6 "cat >> ~/.ssh/authorized_keys"

# 输入密码：Aa121314
```

### 完成后测试

```bash
ssh root@118.194.253.6
# 应该不需要密码直接登录
```

---

## 方法二：手动复制（如果方法一失败）

### 第一步：复制公钥内容

在本地 PowerShell 中执行：

```powershell
cat ~/.ssh/id_rsa.pub
```

复制输出的内容（以 `ssh-rsa` 开头）

### 第二步：登录服务器

```bash
ssh root@118.194.253.6
# 输入密码：Aa121314
```

### 第三步：添加公钥到服务器

在服务器上执行：

```bash
# 创建 .ssh 目录（如果不存在）
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 编辑 authorized_keys 文件
nano ~/.ssh/authorized_keys
```

### 第四步：粘贴公钥

1. 在 nano 编辑器中，粘贴你刚才复制的公钥内容
2. 按 `Ctrl + O` 保存
3. 按 `Enter` 确认
4. 按 `Ctrl + X` 退出

### 第五步：设置权限

```bash
chmod 600 ~/.ssh/authorized_keys
```

### 第六步：退出并测试

```bash
exit
ssh root@118.194.253.6
# 应该不需要密码直接登录
```

---

## 方法三：使用 PowerShell 脚本（一键执行）

创建文件 `setup_ssh_key.ps1`：

```powershell
# 读取公钥
$publicKey = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"

# SSH 命令
$sshCommand = @"
mkdir -p ~/.ssh && \
chmod 700 ~/.ssh && \
echo '$publicKey' >> ~/.ssh/authorized_keys && \
chmod 600 ~/.ssh/authorized_keys && \
echo 'SSH key setup complete'
"@

# 执行
ssh root@118.194.253.6 $sshCommand
```

运行：

```powershell
powershell -ExecutionPolicy Bypass -File setup_ssh_key.ps1
# 输入密码：Aa121314
```

---

## 验证设置

### 测试免密登录

```bash
ssh root@118.194.253.6
```

如果不需要输入密码就能登录，说明设置成功！

### 查看服务器上的公钥

```bash
ssh root@118.194.253.6 "cat ~/.ssh/authorized_keys"
```

应该能看到你的公钥（以 `admin@DESKTOP-LMTQJ4U` 结尾）

---

## 设置成功后

### 1. 测试自动化部署

```bash
cd deploy
python auto_deploy_ssh.py
```

### 2. 或者直接 SSH 执行命令

```bash
ssh root@118.194.253.6 "cd /opt/imap && git pull origin main"
```

---

## 故障排查

### 问题 1: 仍然要求输入密码

**检查服务器配置：**

```bash
ssh root@118.194.253.6

# 检查 SSH 配置
sudo grep "PubkeyAuthentication" /etc/ssh/sshd_config
# 应该是：PubkeyAuthentication yes

# 检查权限
ls -la ~/.ssh/
# authorized_keys 应该是 600 权限
# .ssh 目录应该是 700 权限

# 重启 SSH 服务
sudo systemctl restart sshd
```

### 问题 2: Permission denied (publickey)

**检查本地私钥权限：**

```powershell
# Windows 上检查
icacls $env:USERPROFILE\.ssh\id_rsa
```

### 问题 3: 公钥格式错误

**重新生成 SSH key：**

```bash
ssh-keygen -t rsa -b 4096 -C "admin@DESKTOP-LMTQJ4U"
# 按 Enter 使用默认路径
# 按 Enter 不设置密码（或设置密码）
```

---

## 你的公钥内容

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDZQBctlEu4vqnbqOBX/Xa78xpVNo1Tv6j1ywEGJ6tvC0KnNCOIz4xofgYIMhxS9Jur4eRn2dNL0nxBI4GcG/d0JiMvqsJnNGSr9IN4mGZUdO4JwdRG7MNK/OtEq/LpTy7H/+fInvm4l2cE55fG1Arx8RRSbVbXWU+whxAqG3qt8TFK4plXXBQKV2u+6+sG3hmQMSfvFOcOcyrTwzg7MbjD4yLFm+Ob2aD0SVsC+I1dTeyCUnXMh4LnHTIYJDTqmQ/6mXu2n6X7Evmz2EB0ZEt34nlQdBKb38kMR4D3zedji45kJMbBgIL+zAIOA7r2cOhvKT7GpnnP+ds3qNXVC25nuyg0Mx1TFDtJQvyylkm0e+hxKugeACOfwd20I06JnAu0ObWFSWo2EnZNklMz9kt8YEC+f8IJV7VLhcq4kbhGYAMGtML1Pvx4xvHIQhV9J7l4dHVeF5YUkHjSxB4xa+369EVvJTvgy1EsQc9iW6X/UJESshPSJYcXc0D1ZqGYWbyymWrzzd79z3nwxA0QNeS40x/QU9ndV0tT85L6VdmkR/PzshcexY47VVGT1OTeT4AhtKcaQYTB8glU/H4+PUL5n0Ksp7YhzFPDUb7aLWjy0IK/XboNm7vA5Igqc/DjWz501GcRNOUPdtbPcXEgI16yenSon/MVYiwTKR5fQPGzaw== admin@DESKTOP-LMTQJ4U
```

---

**推荐：** 先尝试方法一（最简单），如果失败再用方法二（手动复制）
