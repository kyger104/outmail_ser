# 服务器部署指南 - JWT 邮箱链接功能

## 服务器信息
- IP: 118.194.253.6
- 用户: root
- 密码: Aa121314

---

## 快速部署（复制粘贴执行）

### 1. SSH 连接服务器

```bash
ssh root@118.194.253.6
# 输入密码: Aa121314
```

### 2. 拉取最新代码

```bash
cd /opt/imap
git pull origin main
```

### 3. 备份并更新数据库

```bash
# 备份数据库
cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup.$(date +%Y%m%d_%H%M%S)

# 更新数据库结构
sqlite3 /opt/imap/data/emails.db "ALTER TABLE mailboxes ADD COLUMN jwt_token VARCHAR(500);"
sqlite3 /opt/imap/data/emails.db "CREATE INDEX idx_mailboxes_jwt_token ON mailboxes(jwt_token);"
```

**注意：** 如果提示字段已存在，说明已经更新过了，可以忽略错误继续。

### 4. 安装新依赖

```bash
cd /opt/imap/backend
source .venv/bin/activate
pip install pyjwt==2.9.0
```

### 5. 重启服务

```bash
systemctl restart imap-backend
```

### 6. 检查服务状态

```bash
# 查看服务状态
systemctl status imap-backend

# 查看日志
journalctl -u imap-backend -n 30 -f
```

按 `Ctrl+C` 退出日志查看。

### 7. 测试 API

```bash
# 测试健康检查
curl http://127.0.0.1:7892/health

# 测试新接口
curl http://127.0.0.1:7892/api/inbox/verify?jwt=test
```

---

## 验证部署

### 1. 测试管理后台

浏览器访问：
```
https://chace123.sbs/admin
```

### 2. 测试 API 文档

浏览器访问：
```
https://chace123.sbs/docs
```

应该能看到新增的接口：
- `GET /api/admin/mailboxes/{id}/link` - 获取邮箱链接
- `GET /api/admin/mailboxes/links` - 批量获取链接
- `GET /api/inbox/verify` - 验证 JWT
- `GET /api/inbox/emails` - 获取邮件列表
- `GET /api/inbox/emails/{email_id}` - 获取邮件详情

### 3. 测试完整流程

1. **导入邮箱**
   ```bash
   curl -X POST "https://chace123.sbs/api/admin/mailboxes/import" \
     -u admin:admin123 \
     -H "Content-Type: application/json" \
     -d '{
       "mailboxes": [
         {"email": "test@outlook.com", "imap_token": "your_app_password"}
       ]
     }'
   ```

2. **获取邮箱链接**
   ```bash
   curl "https://chace123.sbs/api/admin/mailboxes/1/link" -u admin:admin123
   ```

3. **访问邮箱链接**
   - 复制返回的 link
   - 在浏览器中打开
   - 应该能看到邮件列表

---

## 故障排查

### 问题 1: 服务启动失败

```bash
# 查看详细错误
journalctl -u imap-backend -n 50

# 常见原因：
# 1. 端口被占用
netstat -tlnp | grep 7892

# 2. Python 依赖缺失
cd /opt/imap/backend
source .venv/bin/activate
pip install -r requirements.txt

# 3. 数据库权限问题
chmod 644 /opt/imap/data/emails.db
```

### 问题 2: 数据库更新失败

```bash
# 检查字段是否已存在
sqlite3 /opt/imap/data/emails.db "PRAGMA table_info(mailboxes);"

# 如果看到 jwt_token 字段，说明已经更新成功
```

### 问题 3: API 返回 404

```bash
# 检查路由是否注册
grep "inbox.router" /opt/imap/backend/main.py

# 应该看到：
# app.include_router(inbox.router)
```

### 问题 4: JWT 验证失败

```bash
# 检查 secret_key 配置
grep "secret_key" /opt/imap/backend/config.py

# 确保 secret_key 不为空
```

---

## 回滚方案

如果部署出现问题，可以回滚：

```bash
# 1. 停止服务
systemctl stop imap-backend

# 2. 回滚代码
cd /opt/imap
git reset --hard HEAD~1

# 3. 恢复数据库
cp /opt/imap/data/emails.db.backup.YYYYMMDD_HHMMSS /opt/imap/data/emails.db

# 4. 重启服务
systemctl start imap-backend
```

---

## 部署完成后

### 1. 访问管理后台

```
https://chace123.sbs/admin
```

### 2. 导入邮箱

- 格式：`email@outlook.com:app_password`
- 每行一个

### 3. 复制邮箱链接

- 点击"复制链接"按钮
- 链接格式：`https://chace123.sbs/?jwt=eyJhbGc...`

### 4. 分享链接

- 用户打开链接即可查看邮件
- 无需登录
- JWT 有效期 1 年

---

## 安全建议

1. **修改管理员密码**
   ```bash
   vim /opt/imap/backend/config.py
   # 修改 admin_password
   systemctl restart imap-backend
   ```

2. **定期备份数据库**
   ```bash
   # 添加到 crontab
   0 2 * * * cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup.$(date +\%Y\%m\%d)
   ```

3. **监控日志**
   ```bash
   journalctl -u imap-backend -f
   ```

---

**部署时间：** 约 5-10 分钟  
**需要重启：** 是  
**数据丢失风险：** 无（已备份）
