#!/bin/bash
# ============================================================
# setup-ssh-keys.sh
# Distribute SSH keys from Pi 5 to all Pi 3s and Pi 4
# Run ONCE after bootstrap
# ============================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[SSH]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

# Generate SSH key if not exists
if [ ! -f ~/.ssh/id_rsa ]; then
    log "Generating SSH key..."
    ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
fi

log "Distributing SSH keys to all nodes..."

# Pi 3s
for i in 1 2 3 4 5 6 7; do
    IP="192.168.50.$((90+i))"
    USER="pi3-$i"
    echo -n "  pi3-$i ($IP): "
    # Clear old known_hosts entry
    ssh-keygen -f ~/.ssh/known_hosts -R "$IP" 2>/dev/null || true
    # Copy key
    if sshpass -p '1234' ssh-copy-id -o StrictHostKeyChecking=no "$USER@$IP" 2>/dev/null; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
    fi
done

# Pi 4
echo -n "  Pi4 (192.168.50.98): "
ssh-keygen -f ~/.ssh/known_hosts -R "192.168.50.98" 2>/dev/null || true
if sshpass -p '1234' ssh-copy-id -o StrictHostKeyChecking=no "pi@192.168.50.98" 2>/dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌ Failed${NC}"
fi

# Verify connections
log "Verifying passwordless SSH..."
echo ""
for i in 1 2 3 4 5 6 7; do
    echo -n "  pi3-$i: "
    ssh pi3-$i@192.168.50.$((90+i)) "hostname" 2>/dev/null && true || echo "❌ Failed"
done
echo -n "  Pi4: "
ssh pi@192.168.50.98 "hostname" 2>/dev/null && true || echo "❌ Failed"

echo ""
log "SSH setup complete!"
