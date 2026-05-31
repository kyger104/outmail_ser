# 🚀 一键部署命令

## 服务器信息
- IP: 118.194.253.6
- 用户: root
- 密码: Aa121314

---

## 快速部署（复制粘贴执行）

### 第一步：SSH 连接服务器

```bash
ssh root@118.194.253.6
```

输入密码：`Aa121314`

---

### 第二步：执行部署（一次性复制整段）

```bash
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
```

---

## 验证部署

### 1. 检查服务状态
```bash
systemctl status imap-backend
```

应该看到 `Active: active (running)`

### 2. 查看日志
```bash
journalctl -u imap-backend -n 30 --no-pager
```

### 3. 测试 API
```bash
curl http://127.0.0.1:7892/health
curl http://127.0.0.1:7892/docs
```

---

## 浏览器测试

1. **API 文档**: https://chace123.sbs/docs
2. **管理后台**: https://chace123.sbs/admin
3. **收件箱**: https://chace123.sbs/inbox

---

## 如果遇到问题

### 问题 1: 服务启动失败
```bash
# 查看详细错误
journalctl -u imap-backend -n 50

# 检查端口
netstat -tlnp | grep 7892

# 手动启动测试
cd /opt/imap/backend
source .venv/bin/activate
python main.py
```

### 问题 2: 403 错误
```bash
# 检查 Nginx 配置
cat /etc/nginx/sites-enabled/imap

# 检查 Nginx 日志
tail -50 /var/log/nginx/error.log

# 重启 Nginx
systemctl restart nginx
```

### 问题 3: 前端页面空白
```bash
# 检查前端文件
ls -la /var/www/imap/

# 如果需要重新构建前端
cd /opt/imap/frontend
npm install
npm run build
cp -r dist/* /var/www/imap/
```

---

## 回滚方案

如果部署出现问题：

```bash
# 停止服务
systemctl stop imap-backend

# 回滚代码
cd /opt/imap
git reset --hard HEAD~1

# 恢复数据库（找到最新备份）
ls -lt data/emails.db.backup.*
cp data/emails.db.backup.YYYYMMDD_HHMMSS data/emails.db

# 重启服务
systemctl start imap-backend
```

---

**预计时间：** 3-5 分钟  
**风险等级：** 低（已备份数据库）  
**需要重启：** 是（约 3 秒中断）
