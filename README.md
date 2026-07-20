# 🖥️ Edge Computing Cluster — Real-Time Threat Detection
### Cloud Computing SS2026 | Frankfurt University of Applied Sciences
### Prof. Dr. Christian Baun | Group 8

[![Deploy to Pi5](https://github.com/Sapkale26/Cloud_Computing_Project/actions/workflows/deploy-pi5.yml/badge.svg)](https://github.com/Sapkale26/Cloud_Computing_Project/actions/workflows/deploy-pi5.yml)
[![Docs](https://img.shields.io/badge/docs-github--pages-blue)](https://sapkale26.github.io/Cloud_Computing_Project/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Project Overview

A self-contained **edge-computing cluster** built from commodity Raspberry Pis that performs real-time AI-based threat detection. The system demonstrates key cloud computing concepts including distributed computing, parallel processing, container orchestration, AI acceleration, and monitoring.

```
Pi 4 (IMX500 Camera)
    ↓ ZeroMQ (30 fps)
Pi 5 + Hailo AI HAT+ → 59 FPS inference
    ↓ parallel preprocessing
Pi 3 × 7 workers (OpenCV)
    ↓
Backend API → MinIO → React Dashboard
                    → Telegram Alerts
                    → Grafana Monitoring
```

---

## ⚡ Key Metrics

| Metric | Value |
|--------|-------|
| AI Inference (CPU) | 0.7 FPS |
| AI Inference (Hailo HAT+) | **59 FPS** |
| Speedup | **84×** |
| Worker Nodes | 7 × Raspberry Pi 3B |
| HPL Peak Performance | 1.18 GFlops |
| MPI Processes | 28 |
| Total Nodes | 9 |

---

## 🏗️ Hardware

| Device | Model | IP | Role |
|--------|-------|-----|------|
| Pi 5 | Raspberry Pi 5 (8GB) | 192.168.50.1 | Master + Hailo AI HAT+ |
| Pi 4 | Raspberry Pi 4 (4GB) | 192.168.50.98 | IMX500 Camera + ZeroMQ |
| Pi 3-1..7 | Raspberry Pi 3B (1GB) | 192.168.50.91-97 | MPI + k3s Workers |

---

## 🚀 Quick Start

### Prerequisites
- Raspberry Pi 5 with fresh OS (64-bit Bookworm)
- NVMe SSD connected
- All Pi 3s on network

### 1. Clone and Bootstrap
```bash
git clone https://github.com/Sapkale26/Cloud_Computing_Project.git ~/cluster
cd ~/cluster
chmod +x scripts/bootstrap-pi5.sh
./scripts/bootstrap-pi5.sh
```

### 2. Configure All Nodes (Ansible)
```bash
cd infrastructure/ansible
ansible-playbook playbooks/setup-all.yml
```

### 3. Start Everything
```bash
./scripts/start-cluster.sh
```

### 4. Access Services
| Service | URL |
|---------|-----|
| Dashboard | http://192.168.50.1:30080 |
| Grafana | http://192.168.50.1:3000 |
| Prometheus | http://192.168.50.1:9090 |
| MinIO Console | http://192.168.50.1:9001 |
| Backend API | http://192.168.50.1:5000 |

---

## 📁 Repository Structure

```
Cloud_Computing_Project/
├── .github/workflows/          # CI/CD pipelines
├── docs/                       # MkDocs documentation
├── infrastructure/
│   ├── ansible/                # Automated node setup
│   └── kubernetes/             # k3s manifests
├── services/
│   ├── backend/                # Node.js REST API
│   ├── frontend/               # React dashboard
│   ├── pi4-camera/             # ZeroMQ frame sender
│   ├── pi5-inference/          # Hailo AI inference
│   ├── pi3-preprocessing/      # OpenCV worker
│   └── telegram-bot/           # Alert bot
├── benchmarks/
│   ├── mpi/                    # Monte Carlo Pi
│   ├── hpl/                    # LINPACK benchmark
│   └── task-distributor/       # Non-MPI scaling
└── scripts/                    # Utility scripts
```

---

## 📚 Documentation

Full documentation available at: **[https://sapkale26.github.io/Cloud_Computing_Project/](https://sapkale26.github.io/Cloud_Computing_Project/)**

- [Task 1 — Cluster Boot](docs/tasks/task-01-cluster-boot.md)
- [Task 2 — HPL Benchmark](docs/tasks/task-02-hpl.md)
- [Task 3 — MPI](docs/tasks/task-03-mpi.md)
- [Task 4 — Amdahl's & Gustafson's Law](docs/tasks/task-04-scaling-laws.md)
- [Task 5 — Monitoring](docs/tasks/task-05-monitoring.md)
- [Task 6 — Edge AI](docs/tasks/task-06-edge-ai.md)
- [Task 7 — Backend + Kubernetes](docs/tasks/task-07-backend.md)
- [Task 8 — Frontend](docs/tasks/task-08-frontend.md)
- [Task 9 — Telegram Bot](docs/tasks/task-09-telegram.md)

---

## 👥 Team

| Name | Email |
|------|-------|
| Shubhangi Sapkale | shubhangi.sapkale@stud.fra-uas.de |
| Janak Koradiya | janak.koradiya@stud.fra-uas.de |
| Disha Bhuva | disha.bhuva@stud.fra-uas.de |
| Kirti Tarsariya | kirti.tarsariya@stud.fra-uas.de |
| Amina Arshad | amina.arshad@stud.fra-uas.de |
| Purvesh Shapariya | purvesh.shapariya@stud.fra-uas.de |
| Marcos Ortega-Jimenez | marcos.ortega-jimenez@stud.fra-uas.de |

---

## 📄 License

MIT License — see [LICENSE](LICENSE)
