#!/bin/bash
# ============================================================
# bootstrap-pi5.sh
# Run this ONCE on a fresh Pi 5 to set up everything
# Usage: ./scripts/bootstrap-pi5.sh
# ============================================================

set -e  # Exit on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║     Group 8 Edge Cluster — Pi 5 Bootstrap            ║"
echo "║     Cloud Computing SS2026 | Frankfurt UAS           ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── 1. System Update ──────────────────────────────────────
log "Updating system packages..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# ── 2. Install Essential Tools ────────────────────────────
log "Installing essential tools..."
sudo apt-get install -y -qq \
    git curl wget vim nano \
    python3-pip python3-venv \
    dnsmasq sshpass \
    ansible \
    docker.io docker-compose \
    build-essential gcc g++ make \
    net-tools iputils-ping \
    htop iotop \
    openmpi-bin libopenmpi-dev

# ── 3. Configure Static IP for eth0 ───────────────────────
log "Configuring static IP 192.168.50.1 on eth0..."
sudo nmcli con mod "Wired connection 1" \
    ipv4.addresses 192.168.50.1/24 \
    ipv4.method manual 2>/dev/null || true
sudo nmcli con up "Wired connection 1" 2>/dev/null || true
sudo ip addr add 192.168.50.1/24 dev eth0 2>/dev/null || true

# ── 4. Configure dnsmasq ──────────────────────────────────
log "Configuring dnsmasq DHCP server..."
sudo tee /etc/dnsmasq.conf > /dev/null << 'EOF'
interface=eth0
bind-interfaces
dhcp-range=192.168.50.50,192.168.50.150,12h
dhcp-host=b8:27:eb:4b:43:2c,192.168.50.91,pi3-1
dhcp-host=b8:27:eb:39:15:74,192.168.50.92,pi3-2
dhcp-host=b8:27:eb:e7:78:92,192.168.50.93,pi3-3
dhcp-host=b8:27:eb:31:7a:10,192.168.50.94,pi3-4
dhcp-host=b8:27:eb:d4:aa:d7,192.168.50.95,pi3-5
dhcp-host=b8:27:eb:a5:ff:f4,192.168.50.96,pi3-6
dhcp-host=b8:27:eb:e3:a8:e9,192.168.50.97,pi3-7
EOF
sudo systemctl enable dnsmasq
sudo systemctl restart dnsmasq
log "dnsmasq configured ✅"

# ── 5. Enable IP Forwarding (NAT for Pi 3s) ───────────────
log "Enabling IP forwarding for internet sharing..."
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

# Detect internet interface
INTERNET_IF=$(ip route | grep default | awk '{print $5}' | head -1)
log "Internet interface detected: $INTERNET_IF"

sudo iptables -t nat -A POSTROUTING -o $INTERNET_IF -j MASQUERADE
sudo iptables -I FORWARD 1 -i eth0 -o $INTERNET_IF -j ACCEPT
sudo iptables -I FORWARD 2 -i $INTERNET_IF -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT

# ── 6. Mount NVMe SSD ─────────────────────────────────────
log "Setting up NVMe SSD..."
if lsblk | grep -q sda; then
    sudo mkdir -p /mnt/nvme
    # Check if already formatted
    if ! sudo blkid /dev/sda1 &>/dev/null; then
        warn "NVMe not formatted. Formatting..."
        sudo parted /dev/sda --script mklabel gpt
        sudo parted /dev/sda --script mkpart primary ext4 0% 100%
        sudo mkfs.ext4 -F /dev/sda1
    fi
    # Add to fstab if not already there
    if ! grep -q "/dev/sda1" /etc/fstab; then
        # nofail = don't break boot if NVMe has issues
        echo "/dev/sda1 /mnt/nvme ext4 defaults,nofail,x-systemd.device-timeout=10 0 0" | sudo tee -a /etc/fstab
    fi
    sudo mount /mnt/nvme 2>/dev/null || true
    sudo mkdir -p /mnt/nvme/{minio-data,prometheus-data,grafana-data,models,logs}
    sudo chown -R pi:pi /mnt/nvme
    log "NVMe mounted at /mnt/nvme ✅"
else
    warn "No NVMe SSD detected. Skipping..."
fi

# ── 7. Install k3s ────────────────────────────────────────
log "Installing k3s Kubernetes..."
if ! command -v k3s &>/dev/null; then
    curl -sfL https://get.k3s.io | sh -
    sudo systemctl enable k3s
fi
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown pi:pi ~/.kube/config
log "k3s installed ✅"

# ── 8. Install Node.js ────────────────────────────────────
log "Installing Node.js 20..."
if ! command -v node &>/dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi
log "Node.js $(node --version) installed ✅"

# ── 9. Install MinIO ──────────────────────────────────────
log "Installing MinIO..."
if ! command -v minio &>/dev/null; then
    wget -q https://dl.min.io/server/minio/release/linux-arm64/minio
    chmod +x minio
    sudo mv minio /usr/local/bin/
fi
log "MinIO installed ✅"

# ── 10. Install Python packages ───────────────────────────
log "Installing Python packages..."
pip3 install --break-system-packages \
    pyzmq opencv-python-headless \
    requests numpy \
    python-telegram-bot[job-queue] \
    python-dotenv \
    ultralytics

# ── 11. Install Hailo ─────────────────────────────────────
log "Installing Hailo AI HAT+ support..."
sudo apt-get install -y hailo-all 2>/dev/null || warn "Hailo packages not available"

# ── 12. Install node_exporter ─────────────────────────────
log "Installing node_exporter for Prometheus..."
if ! command -v node_exporter &>/dev/null; then
    NODE_EXP_VERSION="1.8.1"
    wget -q "https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXP_VERSION}/node_exporter-${NODE_EXP_VERSION}.linux-arm64.tar.gz"
    tar xzf "node_exporter-${NODE_EXP_VERSION}.linux-arm64.tar.gz"
    sudo cp "node_exporter-${NODE_EXP_VERSION}.linux-arm64/node_exporter" /usr/local/bin/
    rm -rf "node_exporter-${NODE_EXP_VERSION}.linux-arm64"*
fi
log "node_exporter installed ✅"

# ── 13. Generate SSH Key ───────────────────────────────────
log "Setting up SSH keys..."
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
fi
log "SSH key ready ✅"

# ── 14. Install npm packages for backend ──────────────────
log "Installing backend dependencies..."
cd ~/cluster/services/backend
npm install --silent
cd ~

# ── 15. Set up systemd services ───────────────────────────
log "Setting up systemd services..."

# node_exporter service
sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=pi
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Bootstrap Complete! ✅                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  1. Copy SSH keys to Pi 3s:  ./scripts/setup-ssh-keys.sh"
echo "  2. Run Ansible:             cd infrastructure/ansible && ansible-playbook playbooks/setup-all.yml"
echo "  3. Start cluster:           ./scripts/start-cluster.sh"
echo ""
