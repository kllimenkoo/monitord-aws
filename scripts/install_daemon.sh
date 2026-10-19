exec >/var/log/monitord-install.log 2>&1
trap 'aws s3 cp /var/log/monitord-install.log s3://${DAEMON_BUCKET}/install.log' EXIT

APP="monitord"
INSTALL_DIR="/opt/${APP}"
VENV_DIR="${INSTALL_DIR}/venv"
UNIT_FILE="/etc/systemd/system/${APP}.service"

dnf install -y python3.12

mkdir -p "${INSTALL_DIR}"
aws s3 sync s3://${DAEMON_BUCKET} "${INSTALL_DIR}"
python3.12 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"

cat >"${UNIT_FILE}" <<EOF
[Unit]
Description=monitord - lightweight Linux system monitoring daemon
After=network.target

[Service]
Environment=AWS_REGION=eu-north-1
Type=simple
WorkingDirectory=${INSTALL_DIR}
ExecStart="${VENV_DIR}/bin/python3" daemon.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now "${APP}.service"

sleep 10
systemctl status monitord.service >>/var/log/monitord-install.log 2>&1
journalctl -u monitord.service --no-pager >>/var/log/monitord-install.log 2>&1
aws s3 cp /var/log/monitord-install.log s3://${DAEMON_BUCKET}/install.log
