# 🚀 手动部署指南（最简单）

## 第一步：打开 PowerShell 或 CMD

按 `Win + R`，输入 `powershell` 或 `cmd`，回车

---

## 第二步：连接服务器

复制粘贴以下命令：

```bash
ssh root@118.194.253.6
```

提示输入密码时，输入：`Aa121314`

---

## 第三步：执行部署（复制整段，一次性粘贴）

连接成功后，复制下面的**完整命令**，右键粘贴到终端：

```bash
cd /opt/imap && git pull origin main && echo "✓ 代码已更新" && cp data/emails.db data/emails.db.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "✓ 数据库备份（首次运行可能无文件）" && cd backend && source .venv/bin/activate && pip install -r requirements.txt -q && echo "✓ 依赖已安装" && systemctl restart imap-backend && echo "✓ 服务已重启" && sleep 3 && systemctl is-active imap-backend && echo "" && echo "========================================" && echo "测试 API:" && curl -s http://127.0.0.1:7892/health && echo "" && echo "========================================" && echo "✅ 部署完成！" && echo "========================================" && echo "" && echo "访问地址：" && echo "- 管理后台：https://chace123.sbs/admin" && echo "- API 文档：https://chace123.sbs/docs" && echo "- 收件箱：https://chace123.sbs/inbox"
```

---

## 第四步：验证部署

部署完成后，在浏览器中访问：

1. **API 文档**: https://chace123.sbs/docs
2. **管理后台**: https://chace123.sbs/admin  
3. **收件箱**: https://chace123.sbs/inbox

---

## 预期输出

如果部署成功，你会看到：

```
✓ 代码已更新
✓ 数据库备份（首次运行可能无文件）
✓ 依赖已安装
✓ 服务已重启
active
========================================
测试 API:
{"status":"ok"}
========================================
✅ 部署完成！
========================================

访问地址：
- 管理后台：https://chace123.sbs/admin
- API 文档：https://chace123.sbs/docs
- 收件箱：https://chace123.sbs/inbox
```

---

## 如果遇到问题

### 问题 1: git pull 失败
```bash
cd /opt/imap
git status
git reset --hard origin/main
git pull origin main
```

### 问题 2: 服务启动失败
```bash
journalctl -u imap-backend -n 50
```

### 问题 3: 端口被占用
```bash
netstat -tlnp | grep 7892
```

---

**预计时间：** 3-5 分钟  
**操作难度：** ⭐ 简单（复制粘贴即可）
