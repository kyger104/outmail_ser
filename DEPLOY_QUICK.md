# 1G1H Ubuntu 快速部署

适用场景：1 核 1G Ubuntu 服务器，代码通过 GitHub 仓库 `kyger104/outmail_ser` 拉取到服务器，本地只维护部署文件和说明。

## 连接方式

不要在文档或脚本中保存服务器密码。建议在本机生成 SSH key，并把公钥加入服务器：

```bash
ssh-keygen -t ed25519 -C "imap-deploy"
ssh-copy-id -i ~/.ssh/id_ed25519.pub ubuntu@YOUR_SERVER_IP
ssh -i ~/.ssh/id_ed25519 ubuntu@YOUR_SERVER_IP
```

如果服务器禁用了 `ssh-copy-id`，手动把 `~/.ssh/id_ed25519.pub` 的内容追加到服务器的 `~/.ssh/authorized_keys`。

## 首次部署

在服务器上执行：

```bash
apt-get update
apt-get install -y git
git clone https://github.com/kyger104/outmail_ser.git /opt/imap
cd /opt/imap
sudo bash deploy/deploy.sh
```

如果 `/opt/imap` 已经存在但不是 git 仓库，`deploy.sh` 会先把旧目录备份为 `/opt/imap.backup.YYYYmmdd_HHMMSS`，再 clone 仓库，并自动保留旧目录中的 `data/` 和 `backend/.env`。

脚本会完成：

- 安装 Python venv、Node.js/npm、Nginx、curl 等依赖
- 创建 `/opt/imap/backend/.venv`
- 安装 `backend/requirements.txt`
- 生成 `backend/.env`，默认 `SYNC_INTERVAL=300`，SQLite 数据库放在 `/opt/imap/data/emails.db`
- 执行 `npm ci && npm run build`
- 复制 `frontend/dist` 到 `/var/www/imap`
- 安装并重启 `imap-backend.service`
- 如果 `/etc/nginx/sites-available/imap` 不存在，则安装默认 Nginx 站点配置；如果已经存在，会保留现有 HTTPS/证书配置
- reload Nginx
- 执行 `http://127.0.0.1:7892/health` 健康检查

首次部署后请立即修改：

```bash
nano /opt/imap/backend/.env
systemctl restart imap-backend
```

至少修改 `ADMIN_PASSWORD`、`SECRET_KEY`、`ENCRYPTION_KEY`。脚本不会在文档中保存这些值。

## 日常更新

在服务器上执行：

```bash
ssh -i ~/.ssh/id_ed25519 ubuntu@YOUR_SERVER_IP
cd /opt/imap
sudo bash deploy/update_from_git_1g1h.sh
```

更新脚本流程：

1. `git fetch` + `git pull --ff-only`
2. 备份 `/opt/imap/data/emails.db`
3. 安装/更新 Python venv 依赖
4. `npm ci` 并用 `npm run build:server` 构建前端
5. 复制 `frontend/dist` 到 `/var/www/imap`
6. `systemctl restart imap-backend`
7. `nginx -t && systemctl reload nginx`
8. health check

也可以从 Windows PowerShell 远程触发：

```powershell
.\deploy\deploy.ps1 -Server YOUR_SERVER_IP -KeyPath "$env:USERPROFILE\.ssh\id_ed25519"
```

## 验证

```bash
systemctl status imap-backend --no-pager
journalctl -u imap-backend -n 50 --no-pager
curl -fsS http://127.0.0.1:7892/health
nginx -t
```

浏览器访问：

- `http://YOUR_SERVER_IP/`
- `http://YOUR_SERVER_IP/docs`
- `http://YOUR_SERVER_IP/admin`

## 1G1H 注意事项

- 默认使用 SQLite 和单 worker，不建议在 1 核 1G 上开启多 worker。
- 默认 `SYNC_INTERVAL=300`，避免频繁 IMAP 同步占满 CPU/内存。
- 本地/CI 使用 `npm run build` 做类型检查和生产构建；1G1H 服务器更新脚本使用 `npm run build:server`，跳过 `vue-tsc` 以降低内存占用。
- Nginx 只代理 `/api/`，不要写成 `/api`，否则 `/api-keys` 前端页面会被误转发到后端。
- 不建议在生产 `.env` 中继续使用默认管理员密码或示例密钥。
- 更新脚本使用 `git pull --ff-only`；如果服务器上有未提交本地改动，请先处理后再更新。
