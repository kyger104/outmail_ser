$password = "Aa121314"
$server = "root@118.194.253.6"

# 部署命令
$command = @"
cd /opt/imap && \
git pull origin main && \
echo '备份数据库...' && \
cp /opt/imap/data/emails.db /opt/imap/data/emails.db.backup.\$(date +%Y%m%d_%H%M%S) && \
echo '更新数据库结构...' && \
sqlite3 /opt/imap/data/emails.db 'ALTER TABLE mailboxes ADD COLUMN jwt_token VARCHAR(500);' 2>&1 || echo '字段可能已存在' && \
sqlite3 /opt/imap/data/emails.db 'CREATE INDEX idx_mailboxes_jwt_token ON mailboxes(jwt_token);' 2>&1 || echo '索引可能已存在' && \
echo '安装依赖...' && \
cd /opt/imap/backend && source .venv/bin/activate && pip install pyjwt==2.9.0 && \
echo '重启服务...' && \
systemctl restart imap-backend && \
sleep 3 && \
echo '检查服务状态...' && \
systemctl status imap-backend --no-pager | head -20 && \
echo '' && \
echo '测试 API...' && \
curl -s http://127.0.0.1:7892/health && \
echo '' && \
echo '部署完成！'
"@

Write-Host "开始部署到服务器..." -ForegroundColor Cyan
Write-Host ""

# 使用 plink 或 ssh
try {
    # 尝试使用 ssh (Windows 10+)
    $env:SSH_ASKPASS = ""
    echo $password | ssh -o StrictHostKeyChecking=no $server $command
} catch {
    Write-Host "SSH 连接失败，请手动执行以下命令：" -ForegroundColor Red
    Write-Host ""
    Write-Host "ssh $server" -ForegroundColor Yellow
    Write-Host "密码: $password" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "然后执行：" -ForegroundColor Yellow
    Write-Host $command -ForegroundColor White
}
