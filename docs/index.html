<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Group 8 — Edge Threat Monitor (ETM)</title>
<style>
  :root {
    --bg: #f5f4f1;
    --surface: #ffffff;
    --surface2: #faf9f6;
    --border: #e4e1d8;
    --accent: #d4a017;
    --accent2: #7c5cbf;
    --text: #1f2733;
    --text2: #6b7280;
    --text3: #475066;
    --warn: #c9762f;
    --danger: #c14953;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    min-height: 100vh;
  }

  header {
    border-bottom: 1px solid var(--border);
    background: #1f2733;
  }

  .header-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 48px 40px 40px;
  }

  .eyebrow {
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #e6c664;
    margin-bottom: 16px;
  }

  h1 {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: #ffffff;
    margin-bottom: 14px;
  }

  h1 span { color: var(--accent); }

  .tagline {
    font-size: 1.05rem;
    color: #b9c2d0;
    max-width: 640px;
    margin-bottom: 28px;
    line-height: 1.7;
  }

  .header-meta { display: flex; gap: 10px; flex-wrap: wrap; }

  .badge {
    font-size: 0.78rem;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.2);
    color: #dbe0e8;
    background: rgba(255,255,255,0.06);
  }

  .badge.gold   { border-color: var(--accent); color: var(--accent); }
  .badge.violet { border-color: var(--accent2); color: #b7a3ec; }

  .container { max-width: 1280px; margin: 0 auto; padding: 48px 40px; }

  .quick-links {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 56px;
  }

  .quick-link {
    background: var(--surface);
    padding: 20px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    color: var(--text);
    transition: background 0.15s;
  }

  .quick-link:hover { background: var(--surface2); }

  .quick-link-icon { font-size: 1.3rem; flex-shrink: 0; }

  .quick-link-label {
    display: block;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text3);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 2px;
  }

  .quick-link-title { font-size: 0.92rem; font-weight: 600; color: var(--accent2); }

  .section-heading {
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text2);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
  }

  .arch-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 56px; }

  .arch-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 24px; }

  .arch-card h3 {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent2);
    margin-bottom: 14px;
  }

  .node-list { list-style: none; }

  .node-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
  }

  .node-item:last-child { border: none; }

  .node-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
  .node-dot.gold   { background: var(--accent); }
  .node-dot.violet { background: var(--accent2); }
  .node-dot.warn   { background: var(--warn); }

  .node-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 2px;
    font-family: 'Courier New', monospace;
  }

  .node-desc { font-size: 0.82rem; color: var(--text3); line-height: 1.5; }

  .arch-code {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px;
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    color: var(--text3);
    line-height: 1.8;
  }

  .arch-code .c-gold   { color: var(--accent); }
  .arch-code .c-violet { color: var(--accent2); }
  .arch-code .c-warn   { color: var(--warn); }
  .arch-code .c-dim    { color: #9aa1ac; }

  .results-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 56px; }

  .result-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; text-align: center; }

  .result-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent2);
    letter-spacing: -0.02em;
    margin-bottom: 4px;
    font-family: 'Courier New', monospace;
  }

  .result-value.gold { color: var(--accent); }
  .result-value.warn { color: var(--warn); }

  .result-label { font-size: 0.8rem; color: var(--text3); line-height: 1.4; }

  .tasks-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 56px; }

  .task-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    display: block;
    transition: border-color 0.15s, background 0.15s;
  }

  .task-card:hover { background: var(--surface2); border-color: var(--accent2); }

  .task-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--accent2); }

  .task-card.gold::before { background: var(--accent); }
  .task-card.warn::before { background: var(--warn); }
  .task-card.red::before  { background: var(--danger); }

  .task-number {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text2);
    margin-bottom: 8px;
  }

  .task-title { font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 8px; }

  .task-desc { font-size: 0.85rem; color: var(--text3); line-height: 1.6; margin-bottom: 14px; }

  .task-footer { display: flex; align-items: center; justify-content: flex-end; }

  .task-status {
    font-size: 0.72rem;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
    background: rgba(212,160,23,0.12);
    color: #a87a10;
    border: 1px solid rgba(212,160,23,0.35);
  }

  .task-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }

  .tag {
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 4px;
    background: var(--surface2);
    color: var(--text3);
    border: 1px solid var(--border);
  }

  .team-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 8px; }

  .team-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }

  .team-name { font-size: 0.86rem; font-weight: 700; color: var(--text); margin-bottom: 4px; }
  .team-email { font-size: 0.74rem; color: var(--text3); word-break: break-all; }

  footer {
    border-top: 1px solid var(--border);
    background: #1f2733;
    padding: 24px 40px;
    text-align: center;
    font-size: 0.82rem;
    color: #b9c2d0;
    margin-top: 40px;
  }

  footer a { color: var(--accent); text-decoration: none; }

  @media (max-width: 900px) {
    .arch-grid { grid-template-columns: 1fr; }
    .tasks-grid { grid-template-columns: 1fr; }
    .team-grid { grid-template-columns: repeat(2,1fr); }
    .results-grid { grid-template-columns: repeat(2,1fr); }
    .quick-links { grid-template-columns: 1fr; }
    h1 { font-size: 2.1rem; }
    .container, .header-inner { padding: 24px 20px; }
  }
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="eyebrow">Group 8 · Cloud Computing SS2026 · Frankfurt UAS</div>
    <h1>Edge Computing Cluster<br>for Real-Time <span>Threat Detection</span></h1>
    <p class="tagline">
      A 9-node heterogeneous Raspberry Pi cluster running real-time AI threat detection at
      59 FPS on a Hailo accelerator, k3s orchestration, MPI benchmarking, and live
      Telegram alerting — built and benchmarked from scratch.
    </p>
    <div class="header-meta">
      <span class="badge gold">✓ Tasks 1–9 Documented</span>
      <span class="badge violet">Prof. Dr. Christian Baun</span>
      <span class="badge">Cloud Computing SS2026</span>
      <span class="badge">github.com/Sapkale26/Cloud_Computing_Project</span>
    </div>
  </div>
</header>

<div class="container">

  <div class="quick-links">
    <a class="quick-link" href="https://sapkale26.github.io/Cloud_Computing_Project/architecture/">
      <span class="quick-link-icon">🏗️</span>
      <div>
        <span class="quick-link-label">Documentation</span>
        <span class="quick-link-title">System Architecture</span>
      </div>
    </a>
    <a class="quick-link" href="https://sapkale26.github.io/Cloud_Computing_Project/benchmarks/mpi-results/">
      <span class="quick-link-icon">📈</span>
      <div>
        <span class="quick-link-label">Results</span>
        <span class="quick-link-title">MPI &amp; HPL Benchmarks</span>
      </div>
    </a>
    <a class="quick-link" href="https://sapkale26.github.io/Cloud_Computing_Project/tasks/task-08-frontend/">
      <span class="quick-link-icon">🖥️</span>
      <div>
        <span class="quick-link-label">Live System</span>
        <span class="quick-link-title">React Dashboard →</span>
      </div>
    </a>
  </div>

  <div class="section-heading">Cluster Architecture</div>
  <div class="arch-grid">
    <div class="arch-card">
      <h3>Hardware Nodes</h3>
      <ul class="node-list">
        <li class="node-item">
          <span class="node-dot gold"></span>
          <div>
            <div class="node-name">master-node (Pi 5)</div>
            <div class="node-desc">192.168.50.1 · 8GB RAM · Hailo AI HAT+<br>k3s control plane · DHCP/NAT gateway · MinIO · Prometheus · Grafana · AI inference</div>
          </div>
        </li>
        <li class="node-item">
          <span class="node-dot violet"></span>
          <div>
            <div class="node-name">camera-node (Pi 4)</div>
            <div class="node-desc">192.168.50.98 · IMX500 AI Camera<br>ZeroMQ video stream publisher, 30 fps</div>
          </div>
        </li>
        <li class="node-item">
          <span class="node-dot warn"></span>
          <div>
            <div class="node-name">pi3-1 to pi3-7 (Pi 3B)</div>
            <div class="node-desc">192.168.50.91–97 · 1GB RAM each · Cortex-A53 @ 1.2GHz<br>SD card boot · MPI + k3s workers</div>
          </div>
        </li>
      </ul>
    </div>
    <div class="arch-card">
      <h3>Network Topology</h3>
      <div class="arch-code">
<span class="c-dim">Internet (wlan0)</span>
    <span class="c-gold">▼</span>
<span class="c-gold">┌─ Pi 5 — master-node ──────────────────┐</span>
<span class="c-gold">│</span>  eth0 · 192.168.50.1                 <span class="c-gold">│</span>
<span class="c-gold">│</span>  DHCP + NAT gateway · k3s · MPI rank0 <span class="c-gold">│</span>
<span class="c-gold">└─────────────────┬─────────────────────┘</span>
                  <span class="c-dim">│ Gigabit switch</span>
<span class="c-violet">    ┌─────────────┴──────────────────┐</span>
<span class="c-violet">    │   pi4 (camera) · pi3-1..7       │</span>
<span class="c-violet">    │   .98        · .91 – .97       │</span>
<span class="c-violet">    └─────────────────────────────────┘</span>
      </div>
    </div>
  </div>

  <div class="section-heading">Key Results at a Glance</div>
  <div class="results-grid">
    <div class="result-card">
      <div class="result-value">59 FPS</div>
      <div class="result-label">Hailo AI inference<br>vs 0.7 FPS on CPU — 84× speedup</div>
    </div>
    <div class="result-card">
      <div class="result-value gold">12.99</div>
      <div class="result-label">Peak GFlops — HPL benchmark<br>Pi 5 alone, N=7000</div>
    </div>
    <div class="result-card">
      <div class="result-value warn">1.31×</div>
      <div class="result-label">MPI Monte Carlo Pi speedup<br>at 16 processes, 100M points</div>
    </div>
    <div class="result-card">
      <div class="result-value">2.65×</div>
      <div class="result-label">Gustafson speedup<br>28 processes, weak scaling</div>
    </div>
    <div class="result-card">
      <div class="result-value gold">10×</div>
      <div class="result-label">Task Distributor throughput gain<br>18K → 191K px/s, n=1 to n=7</div>
    </div>
    <div class="result-card">
      <div class="result-value warn">44%</div>
      <div class="result-label">Estimated serial fraction<br>SSH + MPI_Reduce overhead</div>
    </div>
  </div>

  <div class="section-heading">Task Overview</div>
  <div class="tasks-grid">

    <a class="task-card" href="https://sapkale26.github.io/Cloud_Computing_Project/tasks/task-01-cluster-boot/">
      <div class="task-number">Task 1</div>
      <div class="task-title">Cluster Provisioning &amp; Boot Setup</div>
      <div class="task-tags">
        <span class="tag">DHCP/NAT</span>
        <span class="tag">SSH keys</span>
        <span class="tag">SD boot</span>
      </div>
      <div class="task-desc">
        Assembled the 9-node cluster on a private LAN with Pi 5 as DHCP/NAT gateway.
        Attempted PXE network boot first, but TFTP bandwidth limits and NFS corruption
        across 7 simultaneous writers pushed the final design to per-node SD cards instead.
      </div>
      <div class="task-footer"><span class="task-status status-done">✓ Complete</span></div>
    </a>

    <a class="task-card gold" href="https://sapkale26.github.io/Cloud_Computing_Project/benchmarks/hpl-results/">
      <div class="task-number">Task 2</div>
      <div class="task-title">HPL / LINPACK Benchmark</div>
      <div class="task-tags">
        <span class="tag">HPL 2.3</span>
        <span class="tag">OpenBLAS</span>
        <span class="tag">N=7000</span>
      </div>
      <div class="task-desc">
        Measured cluster GFlops via the TOP500 standard benchmark across process counts 1–28.
        Pi 5 alone hit the peak at 12.99 GFlops; every additional Pi 3 worker made it slower,
        and np=28 failed its residual check from communication-driven numerical error.
      </div>
      <div class="task-footer"><span class="task-status status-done">✓ Complete</span></div>
    </a>

    <a class="task-card violet" href="https://sapkale26.github.io/Cloud_Computing_Project/benchmarks/mpi-results/">
      <div class="task-number">Task 3</div>
      <div class="task-title">MPI Deployment &amp; Scaling Laws</div>
      <div class="task-tags">
        <span class="tag">OpenMPI 5.0.7</span>
        <span class="tag">Monte Carlo Pi</span>
        <span class="tag">Amdahl</span>
        <span class="tag">Gustafson</span>
      </div>
      <div class="task-desc">
        Two Monte Carlo Pi programs demonstrate both laws: fixed 100M-point runs show Amdahl's
        ceiling (best speedup 1.31× at np=16, s ≈ 44%), while scaling the workload with process
        count shows Gustafson's Law reaching 2.65× at np=28.
      </div>
      <div class="task-footer"><span class="task-status status-done">✓ Complete</span></div>
    </a>

    <a class="task-card warn" href="https://sapkale26.github.io/Cloud_Computing_Project/benchmarks/amdahl-graphs/">
      <div class="task-number">Task 4</div>
      <div class="task-title">Task Distributor (Non-MPI)</div>
      <div class="task-tags">
        <span class="tag">POV-Ray</span>
        <span class="tag">SSH + NFS</span>
        <span class="tag">ImageMagick</span>
      </div>
      <div class="task-desc">
        Prof. Baun's Task Distributor tool split ray-traced renders across workers over SSH/NFS.
        Fixed 800×600 images got slower with more nodes (SSH+NFS overhead &gt; computation),
        while scaling image size with node count raised throughput 10× — 18K to 191K px/s.
      </div>
      <div class="task-footer"><span class="task-status status-done">✓ Complete</span></div>
    </a>

    <a class="task-card" href="https://sapkale26.github.io/Cloud_Computing_Project/tasks/task-05-monitoring/">
      <div class="task-number">Task 5</div>
      <div class="task-title">Monitoring Solution</div>
      <div class="task-tags">
        <span class="tag">Prometheus</span>
        <span class="tag">Grafana</span>
      </div>
      <div class="task-desc">
        Prometheus scrapes per-node CPU, RAM, and temperature metrics from all 9 nodes;
        Grafana dashboards give the team a live view of cluster health during benchmark runs.
      </div>
      <div class="task-footer"><span class="task-status status-done">✓ Complete</span></div>
    </a>

    <a class="task-card gold" href="https://sapkale26.github.io/Cloud_Computing_Project/tasks/task-06-edge-ai/">
      <div class="task-number">Task 6</div>
      <div class="task-title">Edge AI — Threat Detection</div>
      <div class="task-tags">
        <span class="tag">Hailo AI HAT+</span>
        <span class="tag">YOLO</span>
        <span class="tag">ZeroMQ</span>
      </div>
      <div class="task-desc">
        The Pi 4 camera streams frames over ZeroMQ to the Hailo-accelerated Pi 5, which runs
        YOLO inference at 59 FPS — an 84× speedup over the 0.7 FPS CPU baseline — before
        distributing preprocessing across the Pi 3 workers.
      </div>
      <div class="task-footer"><span class="task-status status-done">✓ Complete</span></div>
    </a>

    <a class="task-card violet" href="https://sapkale26.github.io/Cloud_Computing_Project/tasks/task-07-backend/">
      <div class="task-number">Task 7</div>
      <div class="task-title">Backend &amp; Kubernetes</div>
      <div class="task-tags">
        <span class="tag">k3s</span>
        <span class="tag">MinIO</span>
        <span class="tag">REST API</span>
      </div>
      <div class="task-desc">
        The backend currently runs on Pi 5, alongside MinIO for S3-compatible detection image
        storage. We containerized and deployed the frontend on k3s following a Dockerfile →
        Deployment → NodePort pipeline, and planned to extend the same approach to the backend;
        this required mounting an SSH key into the pod for secure node-to-node access, which we
        were unable to get working reliably before the deadline. The backend remains fully
        functional in its current form, and completing the k3s migration is the clear next step.
      </div>
      <div class="task-footer"><span class="task-status status-done">✓ Complete</span></div>
    </a>

    <a class="task-card" href="https://sapkale26.github.io/Cloud_Computing_Project/tasks/task-08-frontend/">
      <div class="task-number">Task 8</div>
      <div class="task-title">Frontend Dashboard</div>
      <div class="task-tags">
        <span class="tag">React</span>
        <span class="tag">Live view</span>
      </div>
      <div class="task-desc">
        A React dashboard surfaces live detections, cluster node health, and alert history
        pulled from the backend API in real time.
      </div>
      <div class="task-footer"><span class="task-status status-done">✓ Complete</span></div>
    </a>

    <a class="task-card red" href="https://sapkale26.github.io/Cloud_Computing_Project/tasks/task-09-telegram/">
      <div class="task-number">Task 9</div>
      <div class="task-title">Telegram Notification Bot</div>
      <div class="task-tags">
        <span class="tag">python-telegram-bot</span>
        <span class="tag">Real-time alerts</span>
      </div>
      <div class="task-desc">
        Polls the backend every 30 seconds and pushes a formatted alert — location, object,
        confidence, and snapshot image — the moment a new threat is detected. Also answers
        /status, /latest, /alerts, and /stats commands on demand.
      </div>
      <div class="task-footer"><span class="task-status status-done">✓ Complete</span></div>
    </a>

  </div>

  <div class="section-heading">Team</div>
  <div class="team-grid">
    <div class="team-card"><div class="team-name">Janak Koradiya</div><div class="team-email">janak.koradiya@stud.fra-uas.de</div></div>
    <div class="team-card"><div class="team-name">Shubhangi Sapkale</div><div class="team-email">shubhangi.sapkale@stud.fra-uas.de</div></div>
    <div class="team-card"><div class="team-name">Disha Bhuva</div><div class="team-email">disha.bhuva@stud.fra-uas.de</div></div>
    <div class="team-card"><div class="team-name">Kirti Tarsariya</div><div class="team-email">kirti.tarsariya@stud.fra-uas.de</div></div>
    <div class="team-card"><div class="team-name">Amina Arshad</div><div class="team-email">amina.arshad@stud.fra-uas.de</div></div>
    <div class="team-card"><div class="team-name">Purvesh Shapariya</div><div class="team-email">purvesh.shapariya@stud.fra-uas.de</div></div>
    <div class="team-card"><div class="team-name">Marcos Ortega-Jimenez</div><div class="team-email">marcos.ortega-jimenez@stud.fra-uas.de</div></div>
  </div>

</div>

<footer>
  Group 8 · Frankfurt University of Applied Sciences · Cloud Computing SS2026 · Prof. Dr. Christian Baun ·
  <a href="https://github.com/Sapkale26/Cloud_Computing_Project">GitHub</a> ·
  <a href="https://sapkale26.github.io/Cloud_Computing_Project/">Documentation</a>
</footer>

</body>
</html>