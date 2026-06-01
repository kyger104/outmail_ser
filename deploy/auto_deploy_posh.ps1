# 自动化部署脚本 - PowerShell 版本
# 使用 Posh-SSH 模块

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "开始自动化部署到服务器" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$server = "118.194.253.6"
$username = "root"
$password = ConvertTo-SecureString "CHANGE_ME_PASSWORD" -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($username, $password)

# 部署命令
$deployCommand = @"
cd /opt/imap && \
git pull origin main && \
echo '✓ 代码已更新' && \
cp data/emails.db data/emails.db.backup.\$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo '✓ 数据库备份（首次运行可能无文件）' && \
cd backend && \
source .venv/bin/activate && \
pip install -r requirements.txt -q && \
echo '✓ 依赖已安装' && \
systemctl restart imap-backend && \
echo '✓ 服务已重启' && \
sleep 3 && \
systemctl is-active imap-backend && \
echo '' && \
echo '========================================' && \
echo '测试 API:' && \
curl -s http://127.0.0.1:7892/health && \
echo '' && \
echo '========================================' && \
echo '✅ 部署完成！' && \
echo '========================================' && \
echo '' && \
echo '访问地址：' && \
echo '- 管理后台：https://chace123.sbs/admin' && \
echo '- API 文档：https://chace123.sbs/docs' && \
echo '- 收件箱：https://chace123.sbs/inbox'
"@

Write-Host "正在连接到服务器 $server..." -ForegroundColor Yellow
Write-Host ""

try {
    # 检查是否安装了 Posh-SSH
    if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
        Write-Host "未安装 Posh-SSH 模块，正在安装..." -ForegroundColor Yellow
        Install-Module -Name Posh-SSH -Force -Scope CurrentUser
        Write-Host "✓ Posh-SSH 已安装" -ForegroundColor Green
    }

    Import-Module Posh-SSH

    # 创建 SSH 会话
    $session = New-SSHSession -ComputerName $server -Credential $credential -AcceptKey

    if ($session) {
        Write-Host "✓ SSH 连接成功" -ForegroundColor Green
        Write-Host ""
        Write-Host "执行部署命令..." -ForegroundColor Yellow
        Write-Host ""

        # 执行命令
        $result = Invoke-SSHCommand -SessionId $session.SessionId -Command $deployCommand

        # 输出结果
        Write-Host $result.Output

        if ($result.ExitStatus -eq 0) {
            Write-Host ""
            Write-Host "============================================================" -ForegroundColor Green
            Write-Host "✅ 部署成功完成！" -ForegroundColor Green
            Write-Host "============================================================" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "============================================================" -ForegroundColor Red
            Write-Host "❌ 部署失败" -ForegroundColor Red
            Write-Host "============================================================" -ForegroundColor Red
            if ($result.Error) {
                Write-Host "错误信息:" -ForegroundColor Red
                Write-Host $result.Error -ForegroundColor Red
            }
        }

        # 关闭会话
        Remove-SSHSession -SessionId $session.SessionId | Out-Null
    } else {
        Write-Host "❌ SSH 连接失败" -ForegroundColor Red
    }

} catch {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "❌ 部署失败" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "错误信息: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动执行以下步骤：" -ForegroundColor Yellow
    Write-Host "1. 打开 PowerShell 或 CMD" -ForegroundColor White
    Write-Host "2. 执行: ssh root@118.194.253.6" -ForegroundColor White
    Write-Host "3. 输入密码: CHANGE_ME_PASSWORD" -ForegroundColor White
    Write-Host "4. 复制粘贴 DEPLOY_QUICK.md 中的部署命令" -ForegroundColor White
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
