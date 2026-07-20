# 🖥️ Edge Computing Cluster — Real-Time Threat Detection

**Cloud Computing SS2026 | Frankfurt University of Applied Sciences**  
**Prof. Dr. Christian Baun | Group 8**

---

## Project Overview

We built a self-contained **edge-computing cluster** using commodity Raspberry Pis to perform real-time AI-based threat detection. The system demonstrates key cloud computing concepts:

- 🖧 **Distributed Computing** — 9-node Raspberry Pi cluster
- ⚡ **AI Acceleration** — Hailo AI HAT+ (59 FPS vs 0.7 FPS on CPU)
- 🔄 **Parallel Processing** — 7 Pi 3 workers for distributed preprocessing
- ☸️ **Container Orchestration** — k3s Kubernetes
- 📊 **Monitoring** — Prometheus + Grafana
- 📦 **Object Storage** — MinIO S3-compatible
- 🤖 **Alerting** — Telegram bot

---

## System Architecture

```
Pi 4 (IMX500 Camera, 30fps)
    ↓ ZeroMQ PUSH
Pi 5 + Hailo AI HAT+ (59 FPS)
    ↓ every 5s: parallel preprocessing
Pi 3-1 ── Pi 3-2 ── Pi 3-3 ── Pi 3-4 ── Pi 3-5 ── Pi 3-6 ── Pi 3-7
    ↓ merged result
Backend API → MinIO → React Dashboard
                    → Telegram Alerts  
                    → Grafana Monitoring
```

---

## Key Performance Metrics

| Metric | Value |
|--------|-------|
| 🚀 Hailo AI Inference | **59 FPS** |
| 🐢 CPU YOLO Inference | 0.7 FPS |
| ⚡ Speedup | **84×** |
| 🖧 Worker Nodes | 7 × Raspberry Pi 3B |
| 📊 HPL Peak | 1.18 GFlops |
| 🔀 MPI Processes | 28 |
| 🖥️ Total Nodes | 9 |

---

## Hardware

| Device | Model | IP | Role |
|--------|-------|-----|------|
| Pi 5 | Raspberry Pi 5 (8GB) | 192.168.50.1 | Master + Hailo AI HAT+ |
| Pi 4 | Raspberry Pi 4 (4GB) | 192.168.50.98 | Camera + ZeroMQ |
| Pi 3-1..7 | Raspberry Pi 3B (1GB) | 192.168.50.91-97 | MPI + k3s Workers |

---

## Quick Links

- [Getting Started](getting-started.md) — Bootstrap the cluster
- [Architecture](architecture.md) — Deep dive into the system design
- [Task 3 — MPI](tasks/task-03-mpi.md) — MPI setup and benchmarks
- [Task 4 — Scaling Laws](tasks/task-04-scaling-laws.md) — Amdahl's & Gustafson's Law
- [Task 5 — Monitoring](tasks/task-05-monitoring.md) — Prometheus + Grafana

---

## Team

| Name | Email |
|------|-------|
| Shubhangi Sapkale | shubhangi.sapkale@stud.fra-uas.de |
| Janak Koradiya | janak.koradiya@stud.fra-uas.de |
| Disha Bhuva | disha.bhuva@stud.fra-uas.de |
| Kirti Tarsariya | kirti.tarsariya@stud.fra-uas.de |
| Amina Arshad | amina.arshad@stud.fra-uas.de |
| Purvesh Shapariya | purvesh.shapariya@stud.fra-uas.de |
| Marcos Ortega-Jimenez | marcos.ortega-jimenez@stud.fra-uas.de |
