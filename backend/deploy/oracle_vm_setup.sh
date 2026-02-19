#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash backend/deploy/oracle_vm_setup.sh /opt/scdis ubuntu
# Defaults:
#   PROJECT_ROOT=/opt/scdis
#   SERVICE_USER=ubuntu

PROJECT_ROOT="${1:-/opt/scdis}"
SERVICE_USER="${2:-ubuntu}"
SERVICE_FILE="/etc/systemd/system/scdis-backend.service"
NGINX_SITE="/etc/nginx/sites-available/scdis"

if [[ ! -d "${PROJECT_ROOT}/backend" ]]; then
  echo "ERROR: backend directory not found at ${PROJECT_ROOT}/backend"
  echo "Clone/copy this repo first, then run again."
  exit 1
fi

install_deps_apt() {
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip nginx
}

install_deps_dnf() {
  sudo dnf install -y python3 python3-pip nginx
}

if command -v apt >/dev/null 2>&1; then
  install_deps_apt
elif command -v dnf >/dev/null 2>&1; then
  install_deps_dnf
else
  echo "ERROR: Neither apt nor dnf found. Install Python3 and nginx manually."
  exit 1
fi

python3 -m venv "${PROJECT_ROOT}/backend/.venv"
"${PROJECT_ROOT}/backend/.venv/bin/pip" install --upgrade pip
"${PROJECT_ROOT}/backend/.venv/bin/pip" install -r "${PROJECT_ROOT}/backend/requirements.txt"

tmp_service="$(mktemp)"
sed "s|__SERVICE_USER__|${SERVICE_USER}|g; s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" \
  "${PROJECT_ROOT}/backend/deploy/scdis-backend.service" > "${tmp_service}"
sudo cp "${tmp_service}" "${SERVICE_FILE}"
rm -f "${tmp_service}"

sudo systemctl daemon-reload
sudo systemctl enable scdis-backend
sudo systemctl restart scdis-backend
sudo systemctl status scdis-backend --no-pager

if [[ -d /etc/nginx/sites-available ]]; then
  sudo cp "${PROJECT_ROOT}/backend/deploy/nginx-scdis.conf" "${NGINX_SITE}"
  sudo sed -i "s|__DOMAIN_OR_IP__|_|g" "${NGINX_SITE}"
  sudo ln -sf "${NGINX_SITE}" /etc/nginx/sites-enabled/scdis
  sudo nginx -t
  sudo systemctl enable nginx
  sudo systemctl restart nginx
else
  echo "Nginx sites-available not found. Configure nginx manually for your distro."
fi

echo
echo "Setup complete."
echo "Backend internal: http://127.0.0.1:8010"
echo "Public via nginx: http://<your-vm-public-ip>/"
echo
echo "Useful commands:"
echo "  sudo journalctl -u scdis-backend -f"
echo "  sudo systemctl restart scdis-backend"
echo "  sudo systemctl restart nginx"
