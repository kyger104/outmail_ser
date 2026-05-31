@echo off
chcp 65001 >nul
echo ==========================================
echo 邮箱管理系统 - 服务器部署
echo ==========================================
echo.

echo 正在连接服务器 118.194.253.6...
echo.

REM 使用 plink (PuTTY) 或 ssh 执行远程命令
REM 需要先安装 PuTTY 或使用 Windows 10+ 自带的 OpenSSH

echo 步骤 1: 拉取最新代码
ssh root@118.194.253.6 "cd /opt/imap && git pull origin main"

echo.
echo 步骤 2: 备份数据库
ssh root@118.194.253.6 "cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup.$(date +%%Y%%m%%d_%%H%%M%%S)"

echo.
echo 步骤 3: 更新数据库结构
ssh root@118.194.253.6 "sqlite3 /opt/imap/data/emails.db 'ALTER TABLE mailboxes ADD COLUMN jwt_token VARCHAR(500);' 2>&1 || echo '字段可能已存在，继续...'"
ssh root@118.194.253.6 "sqlite3 /opt/imap/data/emails.db 'CREATE INDEX idx_mailboxes_jwt_token ON mailboxes(jwt_token);' 2>&1 || echo '索引可能已存在，继续...'"

echo.
echo 步骤 4: 安装新依赖
ssh root@118.194.253.6 "cd /opt/imap/backend && source .venv/bin/activate && pip install pyjwt==2.9.0"

echo.
echo 步骤 5: 重启服务
ssh root@118.194.253.6 "systemctl restart imap-backend"

echo.
echo 步骤 6: 等待服务启动...
timeout /t 3 /nobreak >nul

echo.
echo 步骤 7: 检查服务状态
ssh root@118.194.253.6 "systemctl status imap-backend --no-pager"

echo.
echo 步骤 8: 测试 API
ssh root@118.194.253.6 "curl -s http://127.0.0.1:7892/health"

echo.
echo ==========================================
echo 部署完成！
echo ==========================================
echo.
echo 访问地址：
echo - 管理后台：https://chace123.sbs/admin
echo - API 文档：https://chace123.sbs/docs
echo.
pause
