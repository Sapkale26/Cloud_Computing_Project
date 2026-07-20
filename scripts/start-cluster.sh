#!/bin/bash
# ============================================================
# start-cluster.sh
# Start all services on the cluster
# Run on Pi 5
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[START]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

CLUSTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ""
echo "🚀 Starting Group 8 Edge Cluster..."
echo ""

# ── 1. MinIO ──────────────────────────────────────────────
log "Starting MinIO object storage..."
if ! pgrep -f "minio server" > /dev/null; then
    MINIO_ROOT_USER=admin \
    MINIO_ROOT_PASSWORD=admin123 \
    minio server /mnt/nvme/minio-data \
        --console-address ":9001" \
        --address ":9000" \
        > /mnt/nvme/logs/minio.log 2>&1 &
    sleep 2
    echo "   MinIO API:     http://192.168.50.1:9000"
    echo "   MinIO Console: http://192.168.50.1:9001"
else
    warn "MinIO already running"
fi

# ── 2. Backend ────────────────────────────────────────────
log "Starting backend API..."
sudo kubectl scale deployment backend --replicas=0 2>/dev/null || true
pkill -f "node.*server.js" 2>/dev/null || true
sleep 1
node $CLUSTER_DIR/services/backend/src/server.js \
    > /mnt/nvme/logs/backend.log 2>&1 &
sleep 2
echo "   Backend API: http://192.168.50.1:5000"

# ── 3. Hailo Receiver ─────────────────────────────────────
log "Starting Hailo AI inference receiver..."
pkill -f receiver_hailo 2>/dev/null || true
sleep 1
python3 $CLUSTER_DIR/services/pi5-inference/receiver_hailo.py \
    > /mnt/nvme/logs/hailo.log 2>&1 &
echo "   Hailo ZeroMQ: port 5555"

# ── 4. Telegram Bot ───────────────────────────────────────
log "Starting Telegram alert bot..."
pkill -f "python3.*main.py" 2>/dev/null || true
sleep 1
if [ -f "$CLUSTER_DIR/services/telegram-bot/.env" ]; then
    python3 $CLUSTER_DIR/services/telegram-bot/src/main.py \
        > /mnt/nvme/logs/telegram.log 2>&1 &
    echo "   Telegram: @edge90_monitor_bot"
else
    warn "Telegram .env not found, skipping..."
fi

# ── 5. Monitoring ─────────────────────────────────────────
log "Starting monitoring stack..."

# node_exporter on Pi 5
if ! pgrep -f node_exporter > /dev/null; then
    /usr/local/bin/node_exporter > /mnt/nvme/logs/node_exporter.log 2>&1 &
fi

# node_exporter on all Pi 3s
for i in 1 2 3 4 5 6 7; do
    IP="192.168.50.$((90+i))"
    USER="pi3-$i"
    ssh -o ConnectTimeout=3 $USER@$IP \
        "nohup /usr/local/bin/node_exporter > /tmp/ne.log 2>&1 &" 2>/dev/null || \
        warn "Could not start node_exporter on pi3-$i"
done

# node_exporter on Pi 4
ssh -o ConnectTimeout=3 pi@192.168.50.98 \
    "nohup /usr/local/bin/node_exporter > /tmp/ne.log 2>&1 &" 2>/dev/null || \
    warn "Could not start node_exporter on Pi 4"

# Prometheus
if ! pgrep -f prometheus > /dev/null; then
    cd ~/prometheus-2.53.0.linux-arm64
    ./prometheus \
        --config.file=prometheus.yml \
        --storage.tsdb.path=/mnt/nvme/prometheus-data \
        --web.listen-address=:9090 \
        > /mnt/nvme/logs/prometheus.log 2>&1 &
    cd ~
    echo "   Prometheus: http://192.168.50.1:9090"
else
    warn "Prometheus already running"
fi

# Grafana
if ! pgrep -f "grafana server" > /dev/null; then
    cd ~/grafana-v11.1.0
    ./bin/grafana server \
        --homepath . \
        > /mnt/nvme/logs/grafana.log 2>&1 &
    cd ~
    echo "   Grafana: http://192.168.50.1:3000 (admin/admin)"
else
    warn "Grafana already running"
fi

# ── 6. Auto-scaler ────────────────────────────────────────
log "Starting auto-scaler..."
pkill -f auto_scaler 2>/dev/null || true
python3 $CLUSTER_DIR/scripts/auto_scaler.py \
    > /mnt/nvme/logs/autoscaler.log 2>&1 &

# ── 7. Frontend (Kubernetes) ──────────────────────────────
log "Checking frontend on Kubernetes..."
sudo kubectl get pods 2>/dev/null | grep frontend || warn "Frontend not running in k3s"

# ── 8. Health Check ───────────────────────────────────────
sleep 3
echo ""
echo "═══════════════════════════════════════════════════"
echo "  ✅ Cluster Status"
echo "═══════════════════════════════════════════════════"

check_service() {
    local name=$1
    local url=$2
    if curl -s --connect-timeout 2 "$url" > /dev/null 2>&1; then
        echo "  ✅ $name"
    else
        echo "  ❌ $name — check /mnt/nvme/logs/"
    fi
}

check_service "Backend API    " "http://192.168.50.1:5000/api/stats"
check_service "MinIO          " "http://192.168.50.1:9000/minio/health/live"
check_service "Prometheus     " "http://192.168.50.1:9090/-/healthy"
check_service "Grafana        " "http://192.168.50.1:3000/api/health"
check_service "Frontend       " "http://192.168.50.1:30080"
check_service "node_exporter  " "http://192.168.50.1:9100/metrics"

echo ""
echo "📷 Start Pi 4 camera:"
echo "   ssh pi@192.168.50.98"
echo "   source yolo-env/bin/activate"
echo "   python sender.py"
echo ""
echo "📊 Dashboard: http://192.168.50.1:30080"
echo "═══════════════════════════════════════════════════"
