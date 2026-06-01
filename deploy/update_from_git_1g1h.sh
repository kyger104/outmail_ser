#!/usr/bin/env bash

set -euo pipefail

APP_DIR="${APP_DIR:-/opt/imap}"
FRONTEND_DIR="${FRONTEND_DIR:-/var/www/imap}"
LOG_DIR="${LOG_DIR:-/var/log/imap-backend}"
BRANCH="${BRANCH:-main}"
DEPLOY_USER="${SUDO_USER:-ubuntu}"

if [ "${EUID}" -ne 0 ]; then
    echo "请使用 root 权限运行此脚本"
    exit 1
fi

cd "${APP_DIR}"
git config --global --add safe.directory "${APP_DIR}" || true

if [ ! -d .git ]; then
    echo "${APP_DIR} 不是 git 工作副本，请先运行 deploy/deploy.sh 完成首次部署"
    exit 1
fi

echo "==> 拉取代码"
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git pull --ff-only origin "${BRANCH}"

mkdir -p "${APP_DIR}/data" "${FRONTEND_DIR}" "${LOG_DIR}"

if ! command -v rsync >/dev/null 2>&1; then
    apt-get update
    apt-get install -y rsync
fi

if [ -f "${APP_DIR}/data/emails.db" ]; then
    backup="${APP_DIR}/data/emails.db.backup.$(date +%Y%m%d_%H%M%S)"
    cp "${APP_DIR}/data/emails.db" "${backup}"
    echo "==> 已备份数据库: ${backup}"
fi

echo "==> 更新后端依赖"
cd "${APP_DIR}/backend"
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ ! -f .env ]; then
    cat > .env <<EOF
DATABASE_URL=sqlite:///${APP_DIR}/data/emails.db
IMAP_SERVER=outlook.office365.com
IMAP_PORT=993
SYNC_INTERVAL=300
ADMIN_USERNAME=admin
ADMIN_PASSWORD=CHANGE_ME_AFTER_DEPLOY
ENCRYPTION_KEY=$(openssl rand -hex 16)
SECRET_KEY=$(openssl rand -hex 32)
HOST=0.0.0.0
PORT=7892
EOF
else
    if grep -q '^SYNC_INTERVAL=' .env; then
        sed -i 's/^SYNC_INTERVAL=.*/SYNC_INTERVAL=300/' .env
    else
        printf '\nSYNC_INTERVAL=300\n' >> .env
    fi
fi

echo "==> 构建前端"
cd "${APP_DIR}/frontend"
export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=384}"
npm ci
npm run build:server
rsync -a --delete dist/ "${FRONTEND_DIR}/"

echo "==> 刷新服务配置"
install -m 0644 "${APP_DIR}/deploy/imap-backend.service" /etc/systemd/system/imap-backend.service
if [ ! -f /etc/nginx/sites-available/imap ]; then
    install -m 0644 "${APP_DIR}/deploy/nginx.conf" /etc/nginx/sites-available/imap
else
    echo "==> 保留已有 Nginx 站点配置: /etc/nginx/sites-available/imap"
fi
ln -sfn /etc/nginx/sites-available/imap /etc/nginx/sites-enabled/imap
rm -f /etc/nginx/sites-enabled/default

chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${APP_DIR}"
chown -R www-data:www-data "${APP_DIR}/data" "${FRONTEND_DIR}" "${LOG_DIR}"
if [ -f "${APP_DIR}/backend/.env" ]; then
    chown "${DEPLOY_USER}:www-data" "${APP_DIR}/backend/.env"
    chmod 0640 "${APP_DIR}/backend/.env"
fi

systemctl daemon-reload
systemctl restart imap-backend
nginx -t
systemctl reload nginx

echo "==> 健康检查"
sleep 3
curl -fsS http://127.0.0.1:7892/health
echo
systemctl is-active imap-backend
echo "更新完成"
