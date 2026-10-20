#!/bin/bash
# ==============================================================================
# CloudShield EC2 Bootstrap Script (Amazon Linux 2023)
# ==============================================================================
set -euo pipefail
exec > >(tee -a /var/log/cloudshield-bootstrap.log | logger -t user-data -s 2>/dev/console) 2>&1

echo "=================================================================="
echo "Starting CloudShield EC2 Bootstrap at $(date -u)"
echo "=================================================================="

# 1. Update OS and install runtime dependencies
echo "[1/7] Installing OS packages..."
dnf update -y
dnf install -y python3.11 python3.11-pip git sqlite amazon-cloudwatch-agent

# 2. Clone repository
echo "[2/7] Cloning CloudShield repository..."
APP_DIR="/opt/cloudshield"
rm -rf "${APP_DIR}"
git clone https://github.com/NeeleshUnleashed/CloudShield.git "${APP_DIR}"

# 3. Create virtual environment and install dependencies
echo "[3/7] Setting up Python virtual environment..."
python3.11 -m venv "${APP_DIR}/venv"
"${APP_DIR}/venv/bin/pip" install --upgrade pip
"${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

# 4. Configure live environment variables
echo "[4/7] Writing application environment..."
cat << 'EOF' > "${APP_DIR}/.env"
AWS_MODE=live
AWS_REGION=ap-southeast-2
S3_BUCKET_NAME=cloudshield-artifacts-206238482111-ap-southeast-2
SNS_TOPIC_ARN=arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts
EOF

# Ensure database and log directories exist
mkdir -p "${APP_DIR}/data" "${APP_DIR}/logs"
chmod 755 "${APP_DIR}/data"

# Seed SQLite database baseline
echo "[4b/7] Initializing SQLite schema and seed inventory..."
PYTHONPATH="${APP_DIR}" "${APP_DIR}/venv/bin/python" -c "
from app.db.seed_data import seed_database
seed_database(force_reset=True)
print('Database initialized successfully.')
"

# 5. Set up automated backup script & cron
echo "[5/7] Configuring hourly S3 backup..."
cp "${APP_DIR}/deployment/aws/cloudshield-backup.sh" /usr/local/bin/cloudshield-backup.sh
chmod +x /usr/local/bin/cloudshield-backup.sh

cat << 'EOF' > /etc/cron.d/cloudshield-backup
0 * * * * root /usr/local/bin/cloudshield-backup.sh >> /var/log/cloudshield-backup.log 2>&1
EOF
chmod 644 /etc/cron.d/cloudshield-backup

# 6. Configure CloudWatch Agent for centralized logging
echo "[6/7] Configuring CloudWatch Logs..."
cat << 'EOF' > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/cloudshield.log",
            "log_group_name": "/cloudshield/application",
            "log_stream_name": "app-stdout",
            "retention_in_days": 1
          },
          {
            "file_path": "/var/log/cloudshield-error.log",
            "log_group_name": "/cloudshield/application",
            "log_stream_name": "app-stderr",
            "retention_in_days": 1
          }
        ]
      }
    }
  }
}
EOF

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json || echo "Warning: CloudWatch agent start deferred."

# 7. Create and launch Systemd service
echo "[7/7] Launching CloudShield systemd service..."
cat << 'EOF' > /etc/systemd/system/cloudshield.service
[Unit]
Description=CloudShield Disaster Response Platform
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/cloudshield
EnvironmentFile=/opt/cloudshield/.env
ExecStart=/opt/cloudshield/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=append:/var/log/cloudshield.log
StandardError=append:/var/log/cloudshield-error.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cloudshield
systemctl start cloudshield

# Wait and verify local health endpoint
sleep 3
if curl -sf http://127.0.0.1:8000/api/health > /dev/null; then
    echo "=================================================================="
    echo "SUCCESS: CloudShield service is healthy and running on port 8000!"
    echo "=================================================================="
else
    echo "ERROR: Health check failed. Check /var/log/cloudshield-error.log" >&2
    exit 1
fi
