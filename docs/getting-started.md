# Getting Started

## Prerequisites

- Raspberry Pi 5 with fresh 64-bit Raspberry Pi OS (Bookworm)
- NVMe SSD connected via HAT
- 7× Raspberry Pi 3B with SD cards
- 1× Raspberry Pi 4 with IMX500 AI Camera
- TP-Link TL-SG108E Gigabit switch
- All nodes connected via ethernet

---

## Step 1 — Flash Pi 5 OS

Flash **Raspberry Pi OS 64-bit (Bookworm)** to NVMe SSD using Raspberry Pi Imager:

- Hostname: `raspberrypi`
- Username: `pi`
- Password: `1234`
- Enable SSH: ✅

---

## Step 2 — Clone Repository

```bash
git clone https://github.com/Sapkale26/Cloud_Computing_Project.git ~/cluster
cd ~/cluster
```

---

## Step 3 — Bootstrap Pi 5

```bash
chmod +x scripts/bootstrap-pi5.sh
./scripts/bootstrap-pi5.sh
```

This installs all dependencies, configures dnsmasq, sets up NVMe, and installs k3s.

---

## Step 4 — Setup SSH Keys

```bash
./scripts/setup-ssh-keys.sh
```

This distributes SSH keys from Pi 5 to all Pi 3s and Pi 4.

---

## Step 5 — Configure Worker Nodes

```bash
cd infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/setup-all.yml
```

This installs OpenMPI, OpenCV, node_exporter on all workers.

---

## Step 6 — Start Everything

```bash
./scripts/start-cluster.sh
```

---

## Step 7 — Start Pi 4 Camera

```bash
ssh pi@192.168.50.98
source yolo-env/bin/activate
python sender.py
```

---

## Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Dashboard | http://192.168.50.1:30080 | — |
| Grafana | http://192.168.50.1:3000 | admin/admin |
| Prometheus | http://192.168.50.1:9090 | — |
| MinIO Console | http://192.168.50.1:9001 | admin/admin123 |
| Backend API | http://192.168.50.1:5000 | — |

---

## Health Check

```bash
./scripts/health-check.sh
```
