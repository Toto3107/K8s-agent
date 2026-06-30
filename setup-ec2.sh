#!/bin/bash
# EC2 Bootstrap Script
# Run this ONCE on a fresh Ubuntu 22.04 EC2 instance
# Usage: curl -sSL <raw-github-url>/setup-ec2.sh | bash

set -e

echo "================================================"
echo "  AI Kubernetes Agent — EC2 Setup"
echo "================================================"

# ── 1. System update ────────────────────────────────
echo ""
echo "→ Updating system..."
sudo apt-get update -y
sudo apt-get upgrade -y

# ── 2. Install Docker ───────────────────────────────
echo ""
echo "→ Installing Docker..."
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add ubuntu user to docker group (no sudo needed)
sudo usermod -aG docker ubuntu

# ── 3. Install Docker Compose ───────────────────────
echo ""
echo "→ Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# ── 4. Install kubectl ──────────────────────────────
echo ""
echo "→ Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# ── 5. Clone the repo ───────────────────────────────
echo ""
echo "→ Cloning repository..."
cd ~
git clone https://github.com/${GITHUB_USERNAME}/ai-kubernetes-agent.git || \
  (cd ai-kubernetes-agent && git pull)

# ── 6. Create .env ──────────────────────────────────
echo ""
echo "→ Setting up environment..."
cd ~/ai-kubernetes-agent
if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "⚠  Edit .env and add your OPENROUTER_API_KEY:"
  echo "   nano ~/ai-kubernetes-agent/.env"
fi

# ── 7. Start the app ────────────────────────────────
echo ""
echo "→ Starting application..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "================================================"
echo "✅ Setup complete!"
echo ""
echo "App running at:"
echo "  Frontend → http://$(curl -s ifconfig.me)"
echo "  Backend  → http://$(curl -s ifconfig.me):8000"
echo "  Health   → http://$(curl -s ifconfig.me)/health"
echo ""
echo "Next steps:"
echo "  1. Add OPENROUTER_API_KEY to .env"
echo "  2. Open port 80 and 8000 in EC2 Security Group"
echo "  3. Run: docker-compose -f docker-compose.prod.yml restart"
echo "================================================"
