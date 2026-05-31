#!/bin/bash
# 服务器部署脚本
# 服务器：118.194.253.6
# 用户：root
# 密码：Aa121314

echo "=========================================="
echo "开始部署邮箱管理系统"
echo "=========================================="

# 1. 拉取最新代码
echo ""
echo "步骤 1: 拉取最新代码..."
cd /opt/imap
git pull origin main

# 2. 备份数据库
echo ""
echo "步骤 2: 备份数据库..."
cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup.$(date +%Y%m%d_%H%M%S)

# 3. 更新数据库结构（添加 jwt_token 字段）
echo ""
echo "步骤 3: 更新数据库结构..."
sqlite3 /opt/imap/data/emails.db <<EOF
ALTER TABLE mailboxes ADD COLUMN jwt_token VARCHAR(500);
CREATE INDEX idx_mailboxes_jwt_token ON mailboxes(jwt_token);
.quit
EOF

# 4. 安装新依赖
echo ""
echo "步骤 4: 安装新依赖..."
cd /opt/imap/backend
source .venv/bin/activate
pip install pyjwt==2.9.0

# 5. 重启后端服务
echo ""
echo "步骤 5: 重启后端服务..."
systemctl restart imap-backend

# 6. 检查服务状态
echo ""
echo "步骤 6: 检查服务状态..."
sleep 2
systemctl status imap-backend --no-pager

# 7. 查看最近日志
echo ""
echo "步骤 7: 查看最近日志..."
journalctl -u imap-backend -n 20 --no-pager

# 8. 测试 API
echo ""
echo "步骤 8: 测试 API..."
echo "测试健康检查："
curl -s http://127.0.0.1:7892/health

echo ""
echo "测试 inbox 路由："
curl -s http://127.0.0.1:7892/api/inbox/verify?jwt=test 2>&1 | head -1

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "访问地址："
echo "- 管理后台：https://chace123.sbs/admin"
echo "- API 文档：https://chace123.sbs/docs"
echo ""
echo "下一步："
echo "1. 访问管理后台导入邮箱"
echo "2. 复制邮箱链接"
echo "3. 访问链接查看邮件"
