#!/bin/bash
# SSH密钥自动配置脚本

SERVER="118.194.253.6"
USER="ubuntu"
PASSWORD="CHANGE_ME_PASSWORD"

echo "正在配置SSH密钥到服务器..."

# 使用sshpass自动输入密码并复制公钥
sshpass -p "$PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no "$USER@$SERVER"

if [ $? -eq 0 ]; then
    echo "✓ SSH密钥配置成功！"
    echo "现在可以使用以下命令免密登录："
    echo "  ssh $USER@$SERVER"
else
    echo "✗ 配置失败，请手动配置"
fi
