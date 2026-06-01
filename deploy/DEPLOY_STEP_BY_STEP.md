# 🚀 服务器部署 - 分步指南

## 准备工作

**服务器信息：**
- IP: 118.194.253.6
- 用户: root
- 密码: CHANGE_ME_PASSWORD

---

## 第一步：连接服务器

打开 PowerShell 或 CMD，执行：

```bash
ssh root@118.194.253.6
```

输入密码：`CHANGE_ME_PASSWORD`

---

## 第二步：执行部署（复制整段）

连接成功后，复制粘贴以下**完整命令**（一次性执行）：

```bash
cd /opt/imap && \
git pull origin main && \
echo "✓ 代码已更新" && \
cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup.$(date +%Y%m%d_%H%M%S) && \
echo "✓ 数据库已备份" && \
sqlite3 /opt/imap/data/emails.db "ALTER TABLE mailboxes ADD COLUMN jwt_token VARCHAR(500);" 2>&1 | grep -v "duplicate column name" || echo "✓ jwt_token 字段已添加" && \
sqlite3 /opt/imap/data/emails.db "CREATE INDEX idx_mailboxes_jwt_token ON mailboxes(jwt_token);" 2>&1 | grep -v "already exists" || echo "✓ 索引已创建" && \
cd /opt/imap/backend && \
source .venv/bin/activate && \
pip install pyjwt==2.9.0 -q && \
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
echo "- API 文档：https://chace123.sbs/docs"
```

---

## 第三步：验证部署

### 1. 检查服务状态

```bash
systemctl status imap-backend
```

应该看到 `Active: active (running)`

### 2. 查看日志

```bash
journalctl -u imap-backend -n 30 --no-pager
```

应该没有错误信息

### 3. 测试新接口

```bash
# 测试健康检查
curl http://127.0.0.1:7892/health

# 测试 inbox 路由
curl http://127.0.0.1:7892/api/inbox/verify?jwt=test
```

---

## 第四步：浏览器验证

### 1. 访问 API 文档

打开浏览器访问：
```
https://chace123.sbs/docs
```

应该能看到新增的接口：
- `GET /api/admin/mailboxes/{id}/link`
- `GET /api/admin/mailboxes/links`
- `GET /api/inbox/verify`
- `GET /api/inbox/emails`
- `GET /api/inbox/emails/{email_id}`

### 2. 访问管理后台

```
https://chace123.sbs/admin
```

### 3. 测试完整流程

1. 在管理后台导入邮箱
2. 点击"复制链接"
3. 在新标签页打开链接
4. 应该能看到邮件列表

---

## 常见问题

### Q1: 提示"duplicate column name"

**答：** 这是正常的，说明字段已经存在，可以忽略。

### Q2: 服务启动失败

**排查：**
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

### Q3: API 返回 404

**排查：**
```bash
# 检查路由是否注册
grep "inbox.router" /opt/imap/backend/main.py

# 应该看到：app.include_router(inbox.router)
```

### Q4: 前端页面空白

**排查：**
```bash
# 检查前端文件
ls -la /var/www/imap/

# 如果没有文件，需要构建前端
cd /opt/imap/frontend
npm install
npm run build
cp -r dist/* /var/www/imap/
```

---

## 回滚方案

如果出现问题，可以回滚：

```bash
# 停止服务
systemctl stop imap-backend

# 回滚代码
cd /opt/imap
git reset --hard HEAD~1

# 恢复数据库（找到最新的备份）
ls -lt /opt/imap/data/emails.db.backup.*
cp /opt/imap/data/emails.db.backup.YYYYMMDD_HHMMSS /opt/imap/data/emails.db

# 重启服务
systemctl start imap-backend
```

---

## 部署检查清单

- [ ] SSH 连接成功
- [ ] 代码拉取成功
- [ ] 数据库备份完成
- [ ] 数据库字段添加成功
- [ ] 依赖安装成功
- [ ] 服务重启成功
- [ ] 服务状态正常
- [ ] API 健康检查通过
- [ ] API 文档可访问
- [ ] 管理后台可访问
- [ ] 邮箱链接功能正常

---

**预计时间：** 5 分钟  
**风险等级：** 低（已备份数据库）  
**需要重启：** 是（约 3 秒中断）
