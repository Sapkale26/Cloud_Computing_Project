# Task 5 — Cluster Monitoring (Prometheus + Grafana)

## Overview

We deployed an industry-standard monitoring stack that observes:

- **Hardware health** — CPU temperature, memory usage, disk I/O
- **OS parameters** — CPU usage, load average, process count, file descriptors
- **Network services** — Bandwidth, packet rates, connection counts
- **Application metrics** — Detection rate, FPS, node status

**Stack:**

```
node_exporter (all 9 nodes) → Prometheus (Pi 5) → Grafana (Pi 5)
                                        ↓
                                   Telegram alerts
```

### Why Prometheus + Grafana?

| Alternative | Why we didn't use it |
|--------------|------------------------|
| Nagios | Old, difficult config, no time-series |
| Zabbix | Heavy, requires PostgreSQL/MySQL |
| CheckMK | No ARM packages available |
| DataDog | Commercial, requires internet, expensive |
| Simple cron + file | No query language, no visualization |

**Why Prometheus wins:**

1. **Pull model** — Prometheus reaches out to targets; knows when they're DOWN
2. **PromQL** — Powerful query language for complex metric analysis
3. **Native Kubernetes** — Integrates with k3s monitoring out of the box
4. **Industry standard** — Used by Google, Netflix, SoundCloud, thousands of companies
5. **Free and open source** — No license costs

## Component 1: node_exporter

`node_exporter` is a Prometheus exporter that collects hardware and OS metrics from Linux systems.

### Why node_exporter?

- Designed specifically for Linux
- No configuration needed — starts collecting immediately
- Lightweight: <5MB RAM, <1% CPU overhead
- 40+ metric collectors built-in

### Installation

```bash
# Download on Pi 5
NODE_EXP_VERSION="1.8.1"
wget https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXP_VERSION}/node_exporter-${NODE_EXP_VERSION}.linux-arm64.tar.gz
tar xzf node_exporter-${NODE_EXP_VERSION}.linux-arm64.tar.gz
sudo cp node_exporter-${NODE_EXP_VERSION}.linux-arm64/node_exporter /usr/local/bin/
sudo chmod +x /usr/local/bin/node_exporter

# Deploy to all Pi 3 workers
for i in 1 2 3 4 5 6 7; do
  scp /usr/local/bin/node_exporter pi@192.168.50.$((90+i)):~/
  ssh pi@192.168.50.$((90+i)) \
    "echo '1234' | sudo -S mv ~/node_exporter /usr/local/bin/ && \
     echo '1234' | sudo -S chmod +x /usr/local/bin/node_exporter"
done

# Deploy to Pi 4
scp /usr/local/bin/node_exporter pi@192.168.50.98:~/
ssh pi@192.168.50.98 \
  "echo '1234' | sudo -S mv ~/node_exporter /usr/local/bin/ && \
   echo '1234' | sudo -S chmod +x /usr/local/bin/node_exporter"
```

### Systemd Service (auto-start on boot)

```bash
sudo tee /etc/systemd/system/node_exporter.service << 'EOF'
[Unit]
Description=Prometheus Node Exporter
After=network.target

[Service]
User=pi
ExecStart=/usr/local/bin/node_exporter
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

### Starting node_exporter on All Nodes

```bash
# Pi 5 (via systemd)
sudo systemctl start node_exporter

# All Pi 3s
for i in 1 2 3 4 5 6 7; do
  ssh pi@192.168.50.$((90+i)) \
    "nohup /usr/local/bin/node_exporter > /tmp/ne.log 2>&1 &"
done

# Pi 4
ssh pi@192.168.50.98 \
  "nohup /usr/local/bin/node_exporter > /tmp/ne.log 2>&1 &"

# Verify all running
for i in 1 2 3 4 5 6 7; do
  echo -n "pi3-$i: "
  curl -s --connect-timeout 2 \
    http://192.168.50.$((90+i)):9100/metrics | head -1 || echo "NOT RUNNING"
done
```

### Why Port 9100?

Port 9100 is the de facto standard for node_exporter set by the Prometheus community:

- Prometheus itself: 9090
- node_exporter: 9100
- AlertManager: 9093
- Grafana: 3000

Using standard ports makes integration with other tools seamless.

## Component 2: Prometheus

Prometheus is an open-source time-series database and monitoring system.

### Installation

```bash
cd ~
wget https://github.com/prometheus/prometheus/releases/download/v2.53.0/prometheus-2.53.0.linux-arm64.tar.gz
tar xzf prometheus-2.53.0.linux-arm64.tar.gz
```

### Configuration

`infrastructure/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s      # Pull metrics every 15 seconds
  evaluation_interval: 15s  # Evaluate rules every 15 seconds

scrape_configs:
  - job_name: 'raspberry-cluster'
    static_configs:
      - targets:
          - '192.168.50.1:9100'   # Pi 5 (master)
          - '192.168.50.91:9100'  # Pi 3-1
          - '192.168.50.92:9100'  # Pi 3-2
          - '192.168.50.93:9100'  # Pi 3-3
          - '192.168.50.94:9100'  # Pi 3-4
          - '192.168.50.95:9100'  # Pi 3-5
          - '192.168.50.96:9100'  # Pi 3-6
          - '192.168.50.97:9100'  # Pi 3-7
          - '192.168.50.98:9100'  # Pi 4 (camera)
        labels:
          cluster: 'rpi-group8'
          project: 'cloud-computing-ss2026'
```

### Why 15-second scrape interval?

| Interval | Pros | Cons |
|----------|------|------|
| 1s | High resolution | High CPU + storage overhead |
| 15s | Industry standard, catches MPI spikes | — |
| 60s | Low overhead | Misses short events |

MPI/HPL benchmarks last 17-400 seconds, so 15s captures the full profile.

**Storage calculation:** 9 nodes × ~400 metrics × (1/15s) = 240 samples/second. Each sample ≈ 16 bytes → 3.8 KB/s → 330 MB/day. Reasonable for Pi 5's NVMe SSD.

### Starting Prometheus

```bash
cd ~/prometheus-2.53.0.linux-arm64
./prometheus \
  --config.file=/home/pi/cluster/infrastructure/prometheus.yml \
  --storage.tsdb.path=/mnt/nvme/prometheus-data \
  --web.listen-address=:9090 \
  > /mnt/nvme/logs/prometheus.log 2>&1 &

# Verify
curl -s http://192.168.50.1:9090/-/healthy
# Output: Prometheus Server is Healthy.
```

Access: `http://192.168.50.1:9090`

### Why pull model (Prometheus) vs push model (alternatives)?

- Prometheus knows when a target is DOWN (no data = problem)
- Easier to manage — add a new node by editing one config file
- No configuration needed on monitored nodes
- Prevents metric storms from many nodes pushing simultaneously

## Component 3: Grafana

Grafana is the visualization layer that queries Prometheus and displays dashboards.

### Installation

```bash
wget https://dl.grafana.com/oss/release/grafana-11.1.0.linux-arm64.tar.gz
tar xzf grafana-11.1.0.linux-arm64.tar.gz
```

### Starting Grafana

```bash
cd ~/grafana-v11.1.0
./bin/grafana server > /mnt/nvme/logs/grafana.log 2>&1 &

# Verify
curl -s http://192.168.50.1:3000/api/health
# Output: {"commit":"...","database":"ok","version":"11.1.0"}
```

Access: `http://192.168.50.1:3000` (admin/admin)

### Adding Prometheus Data Source

1. Go to **Connections → Data sources**
2. Click **Add data source**
3. Select **Prometheus**
4. URL: `http://192.168.50.1:9090`
5. Click **Save & Test** → "Successfully queried"

### Import Node Exporter Dashboard

Dashboard ID **1860** ("Node Exporter Full") is downloaded 15+ million times:

1. Dashboards → Import
2. Enter ID: `1860`
3. Click Load
4. Select Prometheus datasource
5. Click Import

This provides 80+ pre-built panels for all node_exporter metrics.

### Key PromQL Queries

**CPU Usage per Node**

```
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)
```

**Memory Usage per Node**

```
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**Network Traffic (eth0)**

```
rate(node_network_receive_bytes_total{device="eth0"}[1m])
rate(node_network_transmit_bytes_total{device="eth0"}[1m])
```

**Temperature**

```
node_thermal_zone_temp / 1000
```

**Load Average**

```
node_load1
node_load5
node_load15
```

**Disk Usage**

```
(1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100
```

## What We Observed During Benchmarks

### During MPI np=28 (Monte Carlo Pi)

| Metric | Pi 5 | Pi 3 workers |
|--------|------|--------------|
| CPU % | 100% | 95-100% |
| Memory | +50MB | +20MB |
| Network | 50-200 Mbps | 50-200 Mbps |
| Temperature | 65-70°C | 55-60°C |

All 9 nodes showing simultaneous CPU spikes confirms all nodes participating in the MPI computation.

### During HPL np=1

| Metric | Pi 5 | Pi 3 workers |
|--------|------|--------------|
| CPU % | 100% (all 4 cores) | ~0% |
| Memory | +800MB | — |
| Network | — | — |

Only Pi 5 shows a CPU spike — confirms np=1 uses only the master node.

### During Task Distributor (7 nodes)

Pi 5 CPU shows brief spikes during (1) SSH connection establishment (serial) and (2) ImageMagick image assembly (serial). Pi 3 CPUs show sustained spikes during POV-Ray rendering (parallel). The timing clearly shows the serial/parallel/serial structure matching Amdahl's Law.

## Why Grafana vs Prometheus UI?

| Feature | Prometheus UI | Grafana |
|---------|-----------------|---------|
| Purpose | Ad-hoc queries | Persistent dashboards |
| Visualization | Line graphs only | Gauges, heatmaps, tables |
| Multiple sources | No | Yes |
| Alerting | No | Yes |
| User management | No | Yes |
| Pre-built dashboards | No | 1000s available |

## Alerting Integration

Grafana alerts are forwarded to Telegram via our alert bot:

```python
# auto_scaler.py monitors CPU via Prometheus API
query = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
cpu = float(resp.json()['data']['result'][0]['value'][1])

if cpu > 70:  # Scale out threshold
    send_telegram(f"⬆️ High CPU: {cpu:.1f}% — adding worker")
```

---
*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Group 8*
