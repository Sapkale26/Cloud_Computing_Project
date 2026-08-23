# Task 1 — Cluster Provisioning & Boot Setup

## Overview

We built a 9-node Raspberry Pi cluster consisting of:

- 1× Raspberry Pi 5 (8GB) — Master node, AI inference, backend
- 1× Raspberry Pi 4 (4GB) — Camera node (IMX500 AI Camera)
- 7× Raspberry Pi 3B (1GB each) — Worker nodes (MPI + Kubernetes)

All nodes are connected via a TP-Link TL-SG108E Gigabit switch on a private LAN (`192.168.50.0/24`).

## Hardware Inventory

| Device | Model | IP Address | MAC Address | Role |
|--------|-------|-----------|--------------|------|
| Pi 5 | Raspberry Pi 5 (8GB) | 192.168.50.1 | 2c:cf:67:20:54:75 | Master + Hailo AI HAT+ |
| Pi 4 | Raspberry Pi 4 (4GB) | 192.168.50.98 | — | Camera + ZeroMQ sender |
| Pi 3-1 | Raspberry Pi 3B (1GB) | 192.168.50.91 | b8:27:eb:4b:43:2c | MPI + k3s worker |
| Pi 3-2 | Raspberry Pi 3B (1GB) | 192.168.50.92 | b8:27:eb:39:15:74 | MPI + k3s worker |
| Pi 3-3 | Raspberry Pi 3B (1GB) | 192.168.50.93 | b8:27:eb:e7:78:92 | MPI + k3s worker |
| Pi 3-4 | Raspberry Pi 3B (1GB) | 192.168.50.94 | b8:27:eb:31:7a:10 | MPI + k3s worker |
| Pi 3-5 | Raspberry Pi 3B (1GB) | 192.168.50.95 | b8:27:eb:d4:aa:d7 | MPI + k3s worker |
| Pi 3-6 | Raspberry Pi 3B (1GB) | 192.168.50.96 | b8:27:eb:a5:ff:f4 | MPI + k3s worker |
| Pi 3-7 | Raspberry Pi 3B (1GB) | 192.168.50.97 | b8:27:eb:e3:a8:e9 | MPI + k3s worker |

## Operating System

All nodes run **Raspberry Pi OS 64-bit (Bookworm)** based on Debian 13.

| Node | Boot Device | OS |
|------|-------------|-----|
| Pi 5 | NVMe SSD (500GB) | 64-bit Bookworm |
| Pi 4 | SD Card | 64-bit Bookworm |
| Pi 3-1..7 | SD Card (individual) | 64-bit Bookworm |

## Network Architecture

```
Internet (wlan0/wlan1)
   |
   Pi 5 (192.168.50.1) ← NAT gateway + DHCP server
   |
   [TL-SG108E Switch]
   |  |  |  |  |  |  |  |
  Pi4 3-1 3-2 3-3 3-4 3-5 3-6 3-7
  .98 .91 .92 .93 .94 .95 .96 .97
```

### DHCP Configuration (dnsmasq)

Pi 5 acts as DHCP server for all nodes. MAC-based static IP assignment ensures consistent addressing.

`/etc/dnsmasq.conf`:

```
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
```

### Static IP Configuration (Pi 5)

Pi 5 `eth0` is configured with a static IP via NetworkManager:

```bash
sudo nmcli con mod "Wired connection 1" \
  ipv4.addresses 192.168.50.1/24 \
  ipv4.method manual
sudo nmcli con up "Wired connection 1"
```

### Internet Sharing (NAT)

Pi 5 shares its WiFi internet connection to all Pi 3 workers via NAT:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

INTERNET_IF=$(ip route | grep default | awk '{print $5}' | head -1)
sudo iptables -t nat -A POSTROUTING -o $INTERNET_IF -j MASQUERADE
sudo iptables -I FORWARD 1 -i eth0 -o $INTERNET_IF -j ACCEPT
sudo iptables -I FORWARD 2 -i $INTERNET_IF -o eth0 \
  -m state --state RELATED,ESTABLISHED -j ACCEPT
```

### SSH Key Distribution

Passwordless SSH from Pi 5 to all nodes enables automated task distribution:

```bash
# Generate key pair on Pi 5
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa

# Distribute to all Pi 3 workers
for i in 1 2 3 4 5 6 7; do
  sshpass -p '1234' ssh-copy-id \
    -o StrictHostKeyChecking=no \
    pi3-$i@192.168.50.$((90+i))
done

# Distribute to Pi 4
sshpass -p '1234' ssh-copy-id \
  -o StrictHostKeyChecking=no \
  pi@192.168.50.98
```

## PXE Boot Attempt (and Why We Switched)

We initially attempted PXE (Preboot Execution Environment) network boot where Pi 3s would boot from the network using TFTP/NFS served by Pi 5.

**Why PXE boot failed:**

1. **TFTP bandwidth bottleneck** — All 7 Pi 3s trying to download an 18MB kernel simultaneously caused timeouts
2. **32-bit vs 64-bit conflict** — Pi 3B GPU bootloader is 32-bit; required special handling
3. **Hostname conflicts** — All nodes had the same hostname when sharing NFS root
4. **NFS corruption** — Multiple simultaneous writers corrupted the shared filesystem
5. **Emergency mode loops** — fstab entries without `nofail` caused boot failures

**Final decision:** SD card boot — each Pi 3 has its own SD card with a complete OS. More reliable, faster boot, and no single point of failure.

**Lesson learned:**

```bash
# Always use nofail for external drives in /etc/fstab
/dev/sda1  /mnt/nvme  ext4  defaults,nofail,x-systemd.device-timeout=10  0  0
```

## Bootstrap Script

The entire Pi 5 setup is automated via `scripts/bootstrap-pi5.sh`:

```bash
git clone https://github.com/Sapkale26/Cloud_Computing_Project.git ~/cluster
cd ~/cluster
chmod +x scripts/bootstrap-pi5.sh
./scripts/bootstrap-pi5.sh
```

This installs: git, dnsmasq, Docker, k3s, Node.js, MinIO, Python packages, Hailo support, node_exporter, OpenMPI.

## Verification

```bash
# Check all nodes are reachable
for i in 1 2 3 4 5 6 7; do
  echo -n "pi3-$i: "
  ping -c 1 -W 1 192.168.50.$((90+i)) > /dev/null 2>&1 \
    && echo "UP ✅" || echo "DOWN ❌"
done

# Full health check
cd ~/cluster && ./scripts/health-check.sh
```

## SSH Credentials

| Node | Username | Password |
|------|----------|----------|
| Pi 5 | pi | 1234 |
| Pi 4 | pi | 1234 |
| Pi 3-1 | pi3-1 | 1234 |
| Pi 3-2 | pi3-2 | 1234 |
| Pi 3-3 | pi3-3 | 1234 |
| Pi 3-4 | pi3-4 | 1234 |
| Pi 3-5 | pi3-5 | 1234 |
| Pi 3-6 | pi3-6 | 1234 |
| Pi 3-7 | pi3-7 | 1234 |

---
*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Group 8*
