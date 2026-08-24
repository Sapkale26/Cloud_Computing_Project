---
title: Group 8 — Edge Computing Cluster
hide:
  - navigation
---

<div class="ec-hero" markdown>

<div class="ec-hero__eyebrow">GROUP 8 · CLOUD COMPUTING SS2026 · FRANKFURT UAS</div>

<div class="ec-hero__title">Edge Computing Cluster<br>for Real-Time <span>Threat Detection</span></div>

<div class="ec-hero__subtitle">
A 9-node Raspberry Pi cluster running real-time AI threat detection at 59 FPS
via a Hailo AI accelerator, k3s orchestration, MPI benchmarking, and live
Telegram alerting — built and benchmarked from scratch.
</div>

<div class="ec-hero__badges">
  <span class="ec-badge ec-badge--accent">✓ 9 Tasks Complete</span>
  <span class="ec-badge">Prof. Dr. Christian Baun</span>
  <span class="ec-badge">Cloud Computing SS2026</span>
  <a class="ec-badge" href="https://github.com/Sapkale26/Cloud_Computing_Project">github.com/Sapkale26/Cloud_Computing_Project</a>
</div>

</div>

<div class="ec-links" markdown>

<a class="ec-card" href="architecture/">
  <div class="ec-card__label">Documentation</div>
  <div class="ec-card__title">System Architecture</div>
</a>

<a class="ec-card" href="benchmarks/mpi-results/">
  <div class="ec-card__label">Results</div>
  <div class="ec-card__title">MPI &amp; HPL Benchmarks</div>
</a>

<a class="ec-card" href="tasks/task-08-frontend/">
  <div class="ec-card__label">Live System</div>
  <div class="ec-card__title">React Dashboard →</div>
</a>

</div>

## Key Performance Metrics

<div class="ec-metrics" markdown>

<div class="ec-metric"><div class="ec-metric__value">59 FPS</div><div class="ec-metric__label">Hailo AI Inference</div></div>
<div class="ec-metric"><div class="ec-metric__value">84×</div><div class="ec-metric__label">Speedup vs CPU</div></div>
<div class="ec-metric"><div class="ec-metric__value">9</div><div class="ec-metric__label">Total Nodes</div></div>
<div class="ec-metric"><div class="ec-metric__value">28</div><div class="ec-metric__label">MPI Processes</div></div>
<div class="ec-metric"><div class="ec-metric__value">1.18</div><div class="ec-metric__label">GFlops (HPL Peak)</div></div>

</div>

## Project Overview

We built a self-contained **edge-computing cluster** using commodity Raspberry Pis to perform real-time AI-based threat detection. The system demonstrates key cloud computing concepts:

- 🖧 **Distributed Computing** — 9-node Raspberry Pi cluster
- ⚡ **AI Acceleration** — Hailo AI HAT+ (59 FPS vs 0.7 FPS on CPU)
- 🔄 **Parallel Processing** — 7 Pi 3 workers for distributed preprocessing
- ☸️ **Container Orchestration** — k3s Kubernetes
- 📊 **Monitoring** — Prometheus + Grafana
- 📦 **Object Storage** — MinIO S3-compatible
- 🤖 **Alerting** — Telegram bot

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

## Hardware

| Device    | Model                 | IP               | Role                   |
| --------- | --------------------- | ---------------- | ----------------------- |
| Pi 5      | Raspberry Pi 5 (8GB)  | 192.168.50.1     | Master + Hailo AI HAT+ |
| Pi 4      | Raspberry Pi 4 (4GB)  | 192.168.50.98    | Camera + ZeroMQ        |
| Pi 3-1..7 | Raspberry Pi 3B (1GB) | 192.168.50.91-97 | MPI + k3s Workers      |

## Team

| Name                  | Email                                 |
| --------------------- | ------------------------------------- |
| Shubhangi Sapkale     | shubhangi.sapkale@stud.fra-uas.de     |
| Janak Koradiya        | janak.koradiya@stud.fra-uas.de        |
| Disha Bhuva           | disha.bhuva@stud.fra-uas.de           |
| Kirti Tarsariya       | kirti.tarsariya@stud.fra-uas.de       |
| Amina Arshad          | amina.arshad@stud.fra-uas.de          |
| Purvesh Shapariya     | purvesh.shapariya@stud.fra-uas.de     |
| Marcos Ortega-Jimenez | marcos.ortega-jimenez@stud.fra-uas.de |

---

*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Group 8*
