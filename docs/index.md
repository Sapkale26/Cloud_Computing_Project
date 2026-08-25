---
title: Edge Computing Cluster
hide:
  - navigation
  - toc
---

<div class="ec-hero" markdown>

<h1 class="ec-hero__title">Edge Computing Cluster<br>for Real-Time <span>Threat Detection</span></h1>

<div class="ec-hero__subtitle">
A 9-node Raspberry Pi cluster running real-time AI threat detection at 59 FPS
via a Hailo AI accelerator, S3-compatible storage via MinIO, a k3s-orchestrated
dashboard, MPI/HPL scalability benchmarking, and live Telegram alerting.
</div>

<div class="ec-hero__badges">
  <span class="ec-badge">Cloud Computing SS2026</span>
  <span class="ec-badge">Prof. Dr. Christian Baun</span>
  <span class="ec-badge ec-badge--accent">✓ Tasks 1–9 Documented</span>
  <span class="ec-badge">Presentation: 26 August 2026</span>
  <a class="ec-badge" href="https://github.com/Sapkale26/Cloud_Computing_Project">github.com/Sapkale26/Cloud_Computing_Project</a>
</div>

</div>

<div class="ec-page" markdown>

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

<div class="ec-section-label">Key Performance Metrics</div>

<div class="ec-metrics" markdown>

<div class="ec-metric"><div class="ec-metric__value">59 FPS</div><div class="ec-metric__label">Hailo AI Inference</div></div>
<div class="ec-metric"><div class="ec-metric__value">84×</div><div class="ec-metric__label">Speedup vs CPU</div></div>
<div class="ec-metric"><div class="ec-metric__value">9</div><div class="ec-metric__label">Total Nodes</div></div>
<div class="ec-metric"><div class="ec-metric__value">28</div><div class="ec-metric__label">MPI Processes</div></div>
<div class="ec-metric"><div class="ec-metric__value">12.99</div><div class="ec-metric__label">GFlops (HPL Peak, Pi 5 alone)</div></div>

</div>

<div class="ec-section-label">Project Overview</div>

<div class="ec-overview" markdown>
We built a self-contained edge-computing cluster using commodity Raspberry Pis to perform real-time AI-based threat detection. The system demonstrates key cloud computing concepts:

🖧 Distributed Computing — 9-node Raspberry Pi cluster
⚡ AI Acceleration — Hailo AI HAT+ (59 FPS vs 0.7 FPS on CPU)
🔄 Parallel Processing — 7 Pi 3 workers for distributed preprocessing
☸️ Container Orchestration — k3s Kubernetes
📊 Monitoring — Prometheus + Grafana
📦 Object Storage — MinIO S3-compatible
🤖 Alerting — Telegram bo
</div>

<div class="ec-section-label">Cluster Architecture</div>

<div class="ec-arch-grid" markdown>

<div class="ec-arch-card" markdown>
<div class="ec-arch-card__title">Network Flow</div>

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

</div>

<div class="ec-arch-card" markdown>
<div class="ec-arch-card__title">Hardware Nodes</div>

<div class="ec-node-list" markdown>

<div class="ec-node" markdown>
<div class="ec-node__name">Pi 5</div>
<div class="ec-node__desc">Raspberry Pi 5 (8GB) · 192.168.50.1 · Master + Hailo AI HAT+</div>
</div>

<div class="ec-node" markdown>
<div class="ec-node__name">Pi 4</div>
<div class="ec-node__desc">Raspberry Pi 4 (4GB) · 192.168.50.98 · Camera + ZeroMQ</div>
</div>

<div class="ec-node" markdown>
<div class="ec-node__name">Pi 3-1..7</div>
<div class="ec-node__desc">Raspberry Pi 3B (1GB) · 192.168.50.91-97 · MPI + k3s Workers</div>
</div>

</div>

</div>

</div>

<div class="ec-section-label">Team</div>

<div class="ec-team-grid" markdown>

<div class="ec-team-card" markdown>
<div class="ec-team-card__name">Shubhangi Sapkale</div>
<div class="ec-team-card__email">shubhangi.sapkale@stud.fra-uas.de</div>
</div>

<div class="ec-team-card" markdown>
<div class="ec-team-card__name">Janak Koradiya</div>
<div class="ec-team-card__email">janak.koradiya@stud.fra-uas.de</div>
</div>

<div class="ec-team-card" markdown>
<div class="ec-team-card__name">Disha Bhuva</div>
<div class="ec-team-card__email">disha.bhuva@stud.fra-uas.de</div>
</div>

<div class="ec-team-card" markdown>
<div class="ec-team-card__name">Kirti Tarsariya</div>
<div class="ec-team-card__email">kirti.tarsariya@stud.fra-uas.de</div>
</div>

<div class="ec-team-card" markdown>
<div class="ec-team-card__name">Amina Arshad</div>
<div class="ec-team-card__email">amina.arshad@stud.fra-uas.de</div>
</div>

<div class="ec-team-card" markdown>
<div class="ec-team-card__name">Purvesh Shapariya</div>
<div class="ec-team-card__email">purvesh.shapariya@stud.fra-uas.de</div>
</div>

<div class="ec-team-card" markdown>
<div class="ec-team-card__name">Marcos Ortega-Jimenez</div>
<div class="ec-team-card__email">marcos.ortega-jimenez@stud.fra-uas.de</div>
</div>

</div>


