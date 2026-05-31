#!/bin/bash

# IMAP 邮件托管系统 - 服务器部署脚本

set -e

echo "========================================="
echo "IMAP 邮件托管系统 - 服务器部署"
echo "========================================="

# 配置变量
INSTALL_DIR="/opt/imap-backend"
FRONTEND_DIR="/var/www/imap-frontend"
LOG_DIR="/var/log/imap-backend"
DATA_DIR="/var/lib/imap-data"

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 权限运行此脚本"
    exit 1
fi

echo ""
echo "1. 安装系统依赖..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx curl

echo ""
echo "2. 创建目录..."
mkdir -p $INSTALL_DIR
mkdir -p $FRONTEND_DIR
mkdir -p $LOG_DIR
mkdir -p $DATA_DIR/attachments

echo ""
echo "3. 部署后端..."
# 复制后端文件
cp -r backend/* $INSTALL_DIR/

# 创建虚拟环境
cd $INSTALL_DIR
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建环境配置
cat > .env << EOF
DATABASE_URL=sqlite:///$DATA_DIR/emails.db
IMAP_SERVER=outlook.office365.com
IMAP_PORT=993
SYNC_INTERVAL=30
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ENCRYPTION_KEY=$(openssl rand -hex 16)
SECRET_KEY=$(openssl rand -hex 32)
HOST=0.0.0.0
PORT=8000
EOF

echo ""
echo "4. 配置 systemd 服务..."
cp imap-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable imap-backend
systemctl start imap-backend

echo ""
echo "5. 部署前端..."
# 安装 Node.js (如果未安装)
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
fi

# 构建前端
cd frontend
npm install
npm run build

# 复制到 nginx 目录
cp -r dist/* $FRONTEND_DIR/

echo ""
echo "6. 配置 Nginx..."
cat > /etc/nginx/sites-available/imap-frontend << 'EOF'
server {
    listen 80;
    server_name _;

    root /var/www/imap-frontend;
    index index.html;

    # 前端路由
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/imap-frontend /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试并重启 Nginx
nginx -t
systemctl restart nginx

echo ""
echo "7. 设置权限..."
chown -R www-data:www-data $INSTALL_DIR
chown -R www-data:www-data $FRONTEND_DIR
chown -R www-data:www-data $LOG_DIR
chown -R www-data:www-data $DATA_DIR

echo ""
echo "========================================="
echo "部署完成！"
echo "========================================="
echo ""
echo "服务状态："
systemctl status imap-backend --no-pager
echo ""
echo "访问地址："
echo "  前端: http://$(hostname -I | awk '{print $1}')"
echo "  API 文档: http://$(hostname -I | awk '{print $1}')/docs"
echo ""
echo "管理员账号："
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "重要文件位置："
echo "  后端代码: $INSTALL_DIR"
echo "  前端代码: $FRONTEND_DIR"
echo "  数据库: $DATA_DIR/emails.db"
echo "  日志: $LOG_DIR"
echo "  配置: $INSTALL_DIR/.env"
echo ""
echo "常用命令："
echo "  查看后端状态: systemctl status imap-backend"
echo "  重启后端: systemctl restart imap-backend"
echo "  查看日志: tail -f $LOG_DIR/error.log"
echo "  重启 Nginx: systemctl restart nginx"
echo ""
