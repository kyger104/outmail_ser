# 邮箱管理系统 - 服务器部署脚本
# 服务器: 118.194.253.6
# 用户: root
# 密码: Aa121314

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "邮箱管理系统 - 服务器部署" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$server = "118.194.253.6"
$user = "root"
$password = "Aa121314"

# 创建部署命令
$deployCommands = @"
cd /opt/imap && \
git pull origin main && \
cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup.\$(date +%Y%m%d_%H%M%S) && \
sqlite3 /opt/imap/data/emails.db 'ALTER TABLE mailboxes ADD COLUMN jwt_token VARCHAR(500);' 2>&1 || true && \
sqlite3 /opt/imap/data/emails.db 'CREATE INDEX idx_mailboxes_jwt_token ON mailboxes(jwt_token);' 2>&1 || true && \
cd /opt/imap/backend && source .venv/bin/activate && pip install pyjwt==2.9.0 && \
systemctl restart imap-backend && \
sleep 3 && \
systemctl status imap-backend --no-pager && \
curl -s http://127.0.0.1:7892/health
"@

Write-Host "正在连接服务器 $server..." -ForegroundColor Yellow
Write-Host ""

# 使用 sshpass 或提示用户手动输入密码
Write-Host "请在 SSH 提示时输入密码: $password" -ForegroundColor Green
Write-Host ""

# 执行部署
ssh "$user@$server" $deployCommands

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "访问地址：" -ForegroundColor Yellow
Write-Host "- 管理后台：https://chace123.sbs/admin" -ForegroundColor White
Write-Host "- API 文档：https://chace123.sbs/docs" -ForegroundColor White
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
