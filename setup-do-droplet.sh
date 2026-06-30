#!/bin/bash
# DigitalOcean Droplet Bootstrap Script
# Run this ONCE on a fresh Ubuntu 22.04 Droplet
# Usage: GITHUB_USERNAME=yourname bash <(curl -sSL https://raw.githubusercontent.com/yourname/ai-kubernetes-agent/main/setup-do-droplet.sh)

set -e

echo "================================================"
echo "  AI Kubernetes Agent — DigitalOcean Setup"
echo "================================================"

# ── 1. System update ────────────────────────────────
echo ""
echo "→ Updating system..."
apt-get update -y
apt-get upgrade -y

# ── 2. Install Docker (DO's official method) ────────
echo ""
echo "→ Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# ── 3. Install Docker Compose plugin ────────────────
echo ""
echo "→ Installing Docker Compose..."
apt-get install -y docker-compose-plugin

# ── 4. Install kubectl ──────────────────────────────
echo ""
echo "→ Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# ── 5. Set up firewall (DigitalOcean uses ufw) ──────
echo ""
echo "→ Configuring firewall..."
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 8000/tcp
ufw --force enable

# ── 6. Clone the repo ───────────────────────────────
echo ""
echo "→ Cloning repository..."
cd ~
if [ -z "$GITHUB_USERNAME" ]; then
  echo "⚠  Set GITHUB_USERNAME env var before running this script"
  echo "   Example: GITHUB_USERNAME=yourname bash setup-do-droplet.sh"
  exit 1
fi

git clone https://github.com/${GITHUB_USERNAME}/ai-kubernetes-agent.git || \
  (cd ai-kubernetes-agent && git pull)

# ── 7. Create .env ──────────────────────────────────
echo ""
echo "→ Setting up environment..."
cd ~/ai-kubernetes-agent
if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "⚠  Edit .env and add your OPENROUTER_API_KEY:"
  echo "   nano ~/ai-kubernetes-agent/.env"
fi

# ── 8. Start the app ────────────────────────────────
echo ""
echo "→ Starting application..."
docker compose -f docker-compose.prod.yml up -d

DROPLET_IP=$(curl -s ifconfig.me)

echo ""
echo "================================================"
echo "✅ Setup complete!"
echo ""
echo "App running at:"
echo "  Frontend → http://${DROPLET_IP}"
echo "  Backend  → http://${DROPLET_IP}:8000"
echo "  Health   → http://${DROPLET_IP}/health"
echo ""
echo "Next steps:"
echo "  1. nano ~/ai-kubernetes-agent/.env"
echo "     → add OPENROUTER_API_KEY"
echo "  2. docker compose -f docker-compose.prod.yml restart"
echo "================================================"
