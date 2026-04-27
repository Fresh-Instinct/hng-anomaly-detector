#!/bin/bash
set -e

echo "🚀 HNG Anomaly Detector - LIVE DEPLOYMENT"

# Ubuntu prep
apt-get update
apt-get install -y docker.io docker-compose iptables net-tools curl htop

# Clone repo
git clone https://github.com/YOUR_USERNAME/hng-anomaly-detector.git .
cd hng-anomaly-detector

# Slack webhook
read -p "Enter Slack Webhook URL: " SLACK_URL
sed -i "s/YOUR_SLACK_WEBHOOK_URL_HERE/$SLACK_URL/g" detector/config.yaml

# Clean deploy
docker-compose down || true
docker system prune -af

# Deploy
docker-compose up -d --build

sleep 60

# Health check
IP=$(curl -s ifconfig.me)
if curl -f http://localhost:8080; then
  echo "✅ SUCCESS!"
  echo "🌐 Nextcloud: http://$IP"
  echo "📊 Dashboard: http://$IP:8080 ← SUBMIT THIS"
  echo "🔍 Logs: docker-compose logs -f detector"
else
  echo "❌ FAILED - check docker-compose logs"
  docker-compose logs
  exit 1
fi
