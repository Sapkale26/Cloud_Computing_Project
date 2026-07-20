#!/bin/bash
# ============================================================
# health-check.sh
# Check status of all cluster services and nodes
# ============================================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok() { echo -e "  ${GREEN}✅ $1${NC}"; }
fail() { echo -e "  ${RED}❌ $1${NC}"; }
warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; }

echo ""
echo "═══════════════════════════════════════════"
echo "  Group 8 Cluster Health Check"
echo "  $(date)"
echo "═══════════════════════════════════════════"

# ── Node Connectivity ─────────────────────────
echo ""
echo "📡 Node Connectivity:"
for i in 1 2 3 4 5 6 7; do
    IP="192.168.50.$((90+i))"
    if ping -c 1 -W 1 $IP > /dev/null 2>&1; then
        ok "pi3-$i ($IP)"
    else
        fail "pi3-$i ($IP) — UNREACHABLE"
    fi
done

if ping -c 1 -W 1 192.168.50.98 > /dev/null 2>&1; then
    ok "Pi4 (192.168.50.98)"
else
    fail "Pi4 (192.168.50.98) — UNREACHABLE"
fi

# ── Services ──────────────────────────────────
echo ""
echo "🔧 Services:"

check_http() {
    local name=$1
    local url=$2
    if curl -sf --connect-timeout 2 "$url" > /dev/null 2>&1; then
        ok "$name"
    else
        fail "$name — DOWN"
    fi
}

check_http "Backend API    " "http://192.168.50.1:5000/api/stats"
check_http "MinIO          " "http://192.168.50.1:9000/minio/health/live"
check_http "Prometheus     " "http://192.168.50.1:9090/-/healthy"
check_http "Grafana        " "http://192.168.50.1:3000/api/health"
check_http "Frontend       " "http://192.168.50.1:30080"

# ── node_exporter ─────────────────────────────
echo ""
echo "📊 node_exporter (metrics):"
check_http "Pi5 :9100      " "http://192.168.50.1:9100/metrics"
for i in 1 2 3 4 5 6 7; do
    check_http "pi3-$i :9100   " "http://192.168.50.$((90+i)):9100/metrics"
done
check_http "Pi4 :9100      " "http://192.168.50.98:9100/metrics"

# ── Kubernetes ────────────────────────────────
echo ""
echo "☸️  Kubernetes (k3s):"
if command -v kubectl > /dev/null; then
    sudo kubectl get nodes --no-headers 2>/dev/null | while read line; do
        name=$(echo $line | awk '{print $1}')
        status=$(echo $line | awk '{print $2}')
        if [ "$status" = "Ready" ]; then
            ok "$name — $status"
        else
            fail "$name — $status"
        fi
    done
else
    warn "kubectl not found"
fi

# ── Processes ─────────────────────────────────
echo ""
echo "⚙️  Processes:"
pgrep -f "node.*server.js" > /dev/null && ok "Backend (Node.js)" || fail "Backend (Node.js)"
pgrep -f "receiver_hailo" > /dev/null && ok "Hailo receiver" || fail "Hailo receiver"
pgrep -f "minio server" > /dev/null && ok "MinIO server" || fail "MinIO server"
pgrep -f "prometheus" > /dev/null && ok "Prometheus" || fail "Prometheus"
pgrep -f "grafana" > /dev/null && ok "Grafana" || fail "Grafana"
pgrep -f "telegram.*main.py" > /dev/null && ok "Telegram bot" || warn "Telegram bot (optional)"
pgrep -f "auto_scaler" > /dev/null && ok "Auto-scaler" || warn "Auto-scaler (optional)"

# ── Disk Usage ────────────────────────────────
echo ""
echo "💾 Disk Usage:"
df -h / | tail -1 | awk '{print "  SD Card:  " $3 " used / " $2 " total (" $5 " used)"}'
df -h /mnt/nvme 2>/dev/null | tail -1 | awk '{print "  NVMe SSD: " $3 " used / " $2 " total (" $5 " used)"}' || warn "NVMe not mounted"

echo ""
echo "═══════════════════════════════════════════"
