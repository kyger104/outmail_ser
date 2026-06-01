# SSH密钥自动配置脚本 (PowerShell版本)

$SERVER = "118.194.253.6"
$USER = "ubuntu"
$PASSWORD = "CHANGE_ME_PASSWORD"
$PUBLIC_KEY = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"

Write-Host "正在配置SSH密钥到服务器..." -ForegroundColor Cyan

# 方法1: 使用ssh-copy-id (如果安装了Git Bash)
Write-Host "`n方法1: 尝试使用 ssh-copy-id..." -ForegroundColor Yellow
$sshCopyId = Get-Command ssh-copy-id -ErrorAction SilentlyContinue
if ($sshCopyId) {
    Write-Host "请在提示时输入密码: $PASSWORD" -ForegroundColor Green
    ssh-copy-id -o StrictHostKeyChecking=no "$USER@$SERVER"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ SSH密钥配置成功！" -ForegroundColor Green
        Write-Host "现在可以使用以下命令免密登录：" -ForegroundColor Cyan
        Write-Host "  ssh $USER@$SERVER" -ForegroundColor White
        exit 0
    }
}

# 方法2: 手动通过SSH命令配置
Write-Host "`n方法2: 手动配置公钥..." -ForegroundColor Yellow
Write-Host "请在提示时输入密码: $PASSWORD" -ForegroundColor Green

$command = @"
mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'SSH密钥已添加'
"@

ssh -o StrictHostKeyChecking=no "$USER@$SERVER" $command

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ SSH密钥配置成功！" -ForegroundColor Green
    Write-Host "现在可以使用以下命令免密登录：" -ForegroundColor Cyan
    Write-Host "  ssh $USER@$SERVER" -ForegroundColor White
} else {
    Write-Host "`n✗ 自动配置失败" -ForegroundColor Red
    Write-Host "`n请使用手动方法（见下方说明）" -ForegroundColor Yellow
}
