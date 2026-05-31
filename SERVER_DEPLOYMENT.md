# 服务器部署指南

## 服务器信息
- **域名：** chace123.sbs
- **IP：** 118.194.253.6
- **配置：** 1H1G + swap
- **DNS：** Cloudflare 代理已启用
- **后端端口：** 7892

---

## 部署架构

```
用户请求
  ↓
https://chace123.sbs (443)
  ↓
Cloudflare CDN/代理
  ↓
Nginx 反向代理 (80/443)
  ↓
FastAPI 后端 (7892)
  ↓
SQLite 数据库
```

---

## 部署步骤

### 1. 准备服务器环境

#### 1.1 连接服务器
```bash
ssh root@118.194.253.6
# 或使用域名
ssh root@chace123.sbs
```

#### 1.2 更新系统
```bash
apt update && apt upgrade -y
```

#### 1.3 安装必要软件
```bash
# Python 3.12
apt install -y python3.12 python3.12-venv python3-pip

# Nginx
apt install -y nginx

# 其他工具
apt install -y git curl wget vim
```

#### 1.4 添加 Swap（1H1G 服务器必须）
```bash
# 创建 2GB swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 验证
free -h
```

---

### 2. 上传项目代码

#### 2.1 创建项目目录
```bash
mkdir -p /opt/imap
cd /opt/imap
```

#### 2.2 上传代码（本地执行）
```bash
# 方法 1：使用 scp
cd D:\DevSpace\H01_hotmail_reg\imap
scp -r backend/ root@118.194.253.6:/opt/imap/
scp -r data/ root@118.194.253.6:/opt/imap/

# 方法 2：使用 Git（推荐）
# 先在本地初始化 git 仓库并推送到 GitHub/Gitee
# 然后在服务器上克隆
git clone https://github.com/your-username/imap.git /opt/imap
```

#### 2.3 验证文件结构
```bash
cd /opt/imap
tree -L 2
# 应该看到：
# /opt/imap/
# ├── backend/
# │   ├── main.py
# │   ├── config.py
# │   ├── models.py
# │   ├── routers/
# │   ├── services/
# │   └── middleware/
# └── data/
```

---

### 3. 配置 Python 环境

#### 3.1 创建虚拟环境
```bash
cd /opt/imap/backend
python3.12 -m venv .venv
source .venv/bin/activate
```

#### 3.2 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3.3 验证安装
```bash
python -c "import fastapi; print(fastapi.__version__)"
python -c "import aioimaplib; print('aioimaplib OK')"
```

---

### 4. 配置环境变量

#### 4.1 创建环境配置文件
```bash
vim /opt/imap/backend/.env
```

#### 4.2 添加配置（按 i 进入编辑模式）
```bash
# 管理员账号（⚠️ 生产环境必须修改）
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-strong-password-here

# 数据库路径
DATABASE_URL=sqlite:///./data/emails.db

# 端口
PORT=7892

# 日志级别
LOG_LEVEL=info
```

按 `Esc` 然后输入 `:wq` 保存退出。

#### 4.3 修改 config.py（如果需要）
```bash
vim /opt/imap/backend/config.py
```

确认端口为 7892：
```python
port: int = 7892
```

---

### 5. 初始化数据库

#### 5.1 创建数据目录
```bash
mkdir -p /opt/imap/data
```

#### 5.2 测试启动（验证配置）
```bash
cd /opt/imap/backend
source .venv/bin/activate
python main.py
```

**预期输出：**
```
INFO: Uvicorn running on http://0.0.0.0:7892
INFO: Application startup complete.
```

按 `Ctrl+C` 停止。

#### 5.3 验证数据库已创建
```bash
ls -lh /opt/imap/data/
# 应该看到 emails.db
```

---

### 6. 配置 Systemd 服务（自动启动）

#### 6.1 创建服务文件
```bash
vim /etc/systemd/system/imap-backend.service
```

#### 6.2 添加配置
```ini
[Unit]
Description=IMAP Email Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/imap/backend
Environment="PATH=/opt/imap/backend/.venv/bin"
ExecStart=/opt/imap/backend/.venv/bin/python main.py
Restart=always
RestartSec=10

# 日志
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 6.3 启用并启动服务
```bash
# 重载 systemd
systemctl daemon-reload

# 启用开机自启
systemctl enable imap-backend

# 启动服务
systemctl start imap-backend

# 查看状态
systemctl status imap-backend
```

**预期输出：**
```
● imap-backend.service - IMAP Email Backend Service
   Loaded: loaded (/etc/systemd/system/imap-backend.service; enabled)
   Active: active (running) since ...
```

#### 6.4 查看日志
```bash
# 实时日志
journalctl -u imap-backend -f

# 最近 100 行
journalctl -u imap-backend -n 100
```

---

### 7. 配置 Nginx 反向代理

#### 7.1 创建 Nginx 配置
```bash
vim /etc/nginx/sites-available/imap
```

#### 7.2 添加配置
```nginx
# HTTP 配置（临时测试用）
server {
    listen 80;
    server_name chace123.sbs;

    # 临时重定向到 HTTPS（稍后配置 SSL 后启用）
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://127.0.0.1:7892;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # API 文档
    location /docs {
        proxy_pass http://127.0.0.1:7892/docs;
        proxy_set_header Host $host;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:7892/health;
        proxy_set_header Host $host;
    }
}
```

#### 7.3 启用配置
```bash
# 创建软链接
ln -s /etc/nginx/sites-available/imap /etc/nginx/sites-enabled/

# 测试配置
nginx -t

# 重载 Nginx
systemctl reload nginx
```

---

### 8. 配置防火墙

#### 8.1 安装 UFW（如果未安装）
```bash
apt install -y ufw
```

#### 8.2 配置规则
```bash
# 允许 SSH（⚠️ 必须先允许，否则会断开连接）
ufw allow 22/tcp

# 允许 HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# 启用防火墙
ufw enable

# 查看状态
ufw status
```

**⚠️ 注意：** 不需要开放 7892 端口，因为 Nginx 反向代理在本地访问。

---

### 9. 配置 HTTPS（Let's Encrypt）

#### 9.1 安装 Certbot
```bash
apt install -y certbot python3-certbot-nginx
```

#### 9.2 获取 SSL 证书

**⚠️ 重要：** 因为你的域名使用了 Cloudflare 代理，需要先**临时关闭代理**：

1. 登录 Cloudflare 控制台
2. 找到 `chace123.sbs` 的 DNS 记录
3. 点击橙色云图标，变成灰色（关闭代理）
4. 等待 2-5 分钟 DNS 生效

然后执行：
```bash
certbot --nginx -d chace123.sbs
```

**交互式问题：**
- Email: 输入你的邮箱（用于证书到期提醒）
- Terms: 输入 `Y` 同意
- Share email: 输入 `N`（可选）
- Redirect HTTP to HTTPS: 输入 `2`（推荐）

**完成后：**
1. 重新打开 Cloudflare 代理（橙色云图标）
2. 在 Cloudflare SSL/TLS 设置中选择 **Full (strict)** 模式

#### 9.3 验证 HTTPS
```bash
curl -I https://chace123.sbs/health
# 应该返回 200 OK
```

#### 9.4 自动续期
```bash
# 测试续期
certbot renew --dry-run

# Certbot 会自动添加 cron 任务，无需手动配置
```

---

### 10. 测试部署

#### 10.1 健康检查
```bash
curl https://chace123.sbs/health
# 预期：{"status":"ok"}
```

#### 10.2 API 文档
浏览器访问：
```
https://chace123.sbs/docs
```

#### 10.3 创建 API Key
```bash
curl -X POST "https://chace123.sbs/api/admin/api-keys" \
  -u admin:your-strong-password-here \
  -H "Content-Type: application/json" \
  -d '{"name":"test-key","description":"测试用","rate_limit":0}'
```

#### 10.4 测试获取邮件
```bash
# 使用真实邮箱和应用密码
curl "https://chace123.sbs/api/GetLastEmails?email=your@outlook.com&password=YOUR_APP_PASSWORD&num=2&boxType=1"
```

---

## 常用运维命令

### 服务管理
```bash
# 查看服务状态
systemctl status imap-backend

# 重启服务
systemctl restart imap-backend

# 停止服务
systemctl stop imap-backend

# 查看日志
journalctl -u imap-backend -f
```

### Nginx 管理
```bash
# 测试配置
nginx -t

# 重载配置
systemctl reload nginx

# 重启 Nginx
systemctl restart nginx

# 查看错误日志
tail -f /var/log/nginx/error.log
```

### 数据库管理
```bash
# 备份数据库
cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup.$(date +%Y%m%d)

# 查看数据库大小
du -h /opt/imap/data/emails.db

# 清理旧备份（保留最近 7 天）
find /opt/imap/data/ -name "emails.db.backup.*" -mtime +7 -delete
```

### 监控资源
```bash
# 内存使用
free -h

# CPU 使用
top

# 磁盘使用
df -h

# 进程监控
ps aux | grep python
```

---

## 故障排查

### 问题 1：服务无法启动
```bash
# 查看详细日志
journalctl -u imap-backend -n 50

# 常见原因：
# 1. 端口被占用
netstat -tlnp | grep 7892

# 2. Python 依赖缺失
cd /opt/imap/backend
source .venv/bin/activate
pip install -r requirements.txt

# 3. 数据库权限问题
chmod 755 /opt/imap/data
chmod 644 /opt/imap/data/emails.db
```

### 问题 2：Nginx 502 Bad Gateway
```bash
# 检查后端服务是否运行
systemctl status imap-backend

# 检查端口监听
netstat -tlnp | grep 7892

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log
```

### 问题 3：HTTPS 证书问题
```bash
# 检查证书状态
certbot certificates

# 手动续期
certbot renew

# 重新获取证书
certbot --nginx -d chace123.sbs --force-renewal
```

### 问题 4：Cloudflare 代理问题
**现象：** 无法获取 SSL 证书或 502 错误

**解决：**
1. 临时关闭 Cloudflare 代理（灰色云）
2. 获取证书或调试
3. 完成后重新开启代理
4. 确保 Cloudflare SSL 模式为 **Full (strict)**

---

## 性能优化

### 1. Nginx 优化
```bash
vim /etc/nginx/nginx.conf
```

添加：
```nginx
# 工作进程数（1H1G 服务器建议 1-2）
worker_processes 1;

# 连接数
events {
    worker_connections 1024;
}

# 启用 gzip 压缩
http {
    gzip on;
    gzip_types text/plain application/json;
    gzip_min_length 1000;
}
```

### 2. 数据库优化
```bash
# 定期清理旧邮件（可选）
# 创建清理脚本
vim /opt/imap/scripts/cleanup.sh
```

```bash
#!/bin/bash
# 删除 30 天前的邮件
sqlite3 /opt/imap/data/emails.db "DELETE FROM emails WHERE received_at < datetime('now', '-30 days');"
echo "Cleanup completed at $(date)"
```

```bash
chmod +x /opt/imap/scripts/cleanup.sh

# 添加 cron 任务（每周执行）
crontab -e
# 添加：
0 2 * * 0 /opt/imap/scripts/cleanup.sh >> /var/log/imap-cleanup.log 2>&1
```

### 3. 日志轮转
```bash
vim /etc/logrotate.d/imap
```

```
/var/log/imap-cleanup.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
```

---

## 安全建议

### 1. 修改管理员密码
```bash
vim /opt/imap/backend/.env
# 修改 ADMIN_PASSWORD
systemctl restart imap-backend
```

### 2. 限制 SSH 访问
```bash
vim /etc/ssh/sshd_config
```

```
# 禁用 root 密码登录（使用密钥）
PermitRootLogin prohibit-password

# 修改 SSH 端口（可选）
Port 2222
```

```bash
systemctl restart sshd
```

### 3. 定期更新
```bash
# 每月执行
apt update && apt upgrade -y
pip install --upgrade -r /opt/imap/backend/requirements.txt
systemctl restart imap-backend
```

### 4. 监控日志
```bash
# 查看异常请求
grep "429" /var/log/nginx/access.log | tail -20

# 查看错误
journalctl -u imap-backend --since "1 hour ago" | grep ERROR
```

---

## 备份策略

### 自动备份脚本
```bash
vim /opt/imap/scripts/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/imap/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/imap/data/emails.db $BACKUP_DIR/emails_$DATE.db

# 备份配置
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/imap/backend/.env /etc/nginx/sites-available/imap

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /opt/imap/scripts/backup.sh

# 每天凌晨 3 点备份
crontab -e
# 添加：
0 3 * * * /opt/imap/scripts/backup.sh >> /var/log/imap-backup.log 2>&1
```

---

## 快速命令汇总

```bash
# 服务管理
systemctl status imap-backend    # 查看状态
systemctl restart imap-backend   # 重启服务
journalctl -u imap-backend -f    # 查看日志

# Nginx 管理
nginx -t                          # 测试配置
systemctl reload nginx            # 重载配置

# 测试 API
curl https://chace123.sbs/health  # 健康检查
curl https://chace123.sbs/docs    # API 文档

# 数据库备份
cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup

# 查看资源
free -h                           # 内存
df -h                             # 磁盘
top                               # CPU
```

---

## 部署检查清单

部署完成后，逐项检查：

- [ ] 服务器可以 SSH 连接
- [ ] Swap 已添加（`free -h` 验证）
- [ ] Python 环境已安装（`python3.12 --version`）
- [ ] 项目代码已上传
- [ ] 依赖已安装（`pip list`）
- [ ] 环境变量已配置（`.env` 文件）
- [ ] 数据库已初始化（`emails.db` 存在）
- [ ] Systemd 服务已启动（`systemctl status imap-backend`）
- [ ] Nginx 配置已生效（`nginx -t`）
- [ ] 防火墙已配置（`ufw status`）
- [ ] HTTPS 证书已获取（`certbot certificates`）
- [ ] Cloudflare 代理已启用（橙色云）
- [ ] 健康检查通过（`curl https://chace123.sbs/health`）
- [ ] API 文档可访问（浏览器打开 `/docs`）
- [ ] 管理员密码已修改（生产环境）
- [ ] 备份脚本已配置（可选）

---

**部署完成！** 🎉

**访问地址：**
- API 文档：https://chace123.sbs/docs
- 健康检查：https://chace123.sbs/health
- 获取邮件：https://chace123.sbs/api/GetLastEmails

**下一步：**
1. 生成应用密码（参考 `HOW_TO_GET_APP_PASSWORD.md`）
2. 测试真实邮箱获取
3. 前端开发（参考 `FRONTEND_DEV_TASK.md`）
