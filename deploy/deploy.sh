#!/usr/bin/env bash

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/kyger104/outmail_ser.git}"
APP_DIR="${APP_DIR:-/opt/imap}"
FRONTEND_DIR="${FRONTEND_DIR:-/var/www/imap}"
LOG_DIR="${LOG_DIR:-/var/log/imap-backend}"
BRANCH="${BRANCH:-main}"
DEPLOY_USER="${SUDO_USER:-ubuntu}"

if [ "${EUID}" -ne 0 ]; then
    echo "请使用 root 权限运行此脚本"
    exit 1
fi

echo "==> 安装系统依赖"
apt-get update
apt-get install -y git python3 python3-pip python3-venv nginx curl ca-certificates rsync openssl

if ! command -v node >/dev/null 2>&1; then
    echo "==> 安装 Node.js 20"
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

echo "==> 准备代码目录: ${APP_DIR}"
if [ ! -d "${APP_DIR}/.git" ]; then
    mkdir -p "$(dirname "${APP_DIR}")"
    if [ -d "${APP_DIR}" ] && [ "$(find "${APP_DIR}" -mindepth 1 -maxdepth 1 | head -n 1)" ]; then
        backup_dir="${APP_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "==> 检测到已有非 git 目录，备份到: ${backup_dir}"
        mv "${APP_DIR}" "${backup_dir}"
        git clone --branch "${BRANCH}" "${REPO_URL}" "${APP_DIR}"
        if [ -d "${backup_dir}/data" ]; then
            rm -rf "${APP_DIR}/data"
            cp -a "${backup_dir}/data" "${APP_DIR}/data"
        fi
        if [ -f "${backup_dir}/backend/.env" ]; then
            cp -a "${backup_dir}/backend/.env" "${APP_DIR}/backend/.env"
        fi
    else
        git clone --branch "${BRANCH}" "${REPO_URL}" "${APP_DIR}"
    fi
fi

cd "${APP_DIR}"
git config --global --add safe.directory "${APP_DIR}" || true
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git pull --ff-only origin "${BRANCH}"

mkdir -p "${APP_DIR}/data" "${FRONTEND_DIR}" "${LOG_DIR}"

echo "==> 准备后端 venv"
cd "${APP_DIR}/backend"
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ ! -f .env ]; then
    echo "==> 生成 backend/.env，请部署后修改管理员密码"
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

echo "==> 安装 systemd 和 Nginx 配置"
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
systemctl enable imap-backend
systemctl restart imap-backend
nginx -t
systemctl reload nginx

echo "==> 健康检查"
sleep 3
curl -fsS http://127.0.0.1:7892/health
echo

echo "部署完成"
echo "应用目录: ${APP_DIR}"
echo "前端目录: ${FRONTEND_DIR}"
echo "后端配置: ${APP_DIR}/backend/.env"
echo "请确认已修改 ADMIN_PASSWORD、SECRET_KEY、ENCRYPTION_KEY。"
