param(
    [Parameter(Mandatory = $true)]
    [string]$Server,

    [string]$User = "ubuntu",
    [string]$KeyPath = "$env:USERPROFILE\.ssh\id_ed25519",
    [string]$AppDir = "/opt/imap",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

Write-Host "使用 SSH key 登录服务器并触发 1G1H 更新流程" -ForegroundColor Cyan
Write-Host "Server: $User@$Server" -ForegroundColor Cyan
Write-Host "Key: $KeyPath" -ForegroundColor Cyan
Write-Host ""

$remoteCommand = "cd '$AppDir' && sudo BRANCH='$Branch' bash deploy/update_from_git_1g1h.sh"

ssh -i $KeyPath "$User@$Server" $remoteCommand

Write-Host ""
Write-Host "更新命令已执行。请检查上方 health check 输出。" -ForegroundColor Green
