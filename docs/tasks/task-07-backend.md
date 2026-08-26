# Task 7 — Backend, Storage & Kubernetes

**Cloud Computing SS2026 | Group 8 | Frankfurt UAS**

**Led by:**

| Component | Lead | Scope |
|---|---|---|
| API & Real-Time Layer | Purvesh | Express setup, detection/stats/alerts endpoints, WebSocket server + broadcast, frame/stream endpoints |
| Storage & Node Monitoring | Shubhangi | MinIO integration (save/cleanup), SSH-based node health polling, worker/preprocess endpoints |
| k3s Kubernetes | Janak | Frontend containerization and Deployment on k3s (see Task 8) |

!!! abstract "At a Glance"
    **Objective:** Build the backend infrastructure that manages the sensor nodes and the collected data — a REST + WebSocket API and S3-compatible object storage for detection images, with Kubernetes-based deployment where implemented.

    **Status:** The backend API and MinIO both run bare-metal on Pi 5. Only the frontend (Task 8) is deployed on k3s today. A k3s deployment of the backend is a work in progress — see [Deployment Status](#deployment-status) below.

---

## Overview

Task 7 covers three pieces of infrastructure, all currently hosted on Pi 5:

- A **Node.js + Express REST API** with a separate **WebSocket server** for live push updates
- **MinIO**, S3-compatible object storage, for detection images
- **k3s** (lightweight Kubernetes), used in this project for the **frontend** deployment (Task 8)

The assignment specification asks for the backend itself to run as Docker container(s) on a k3s cluster, forming a robust, high-availability cluster of the Raspberry Pi 3 nodes, with the storage service included in that cluster. What we actually built differs from that in one specific way, described plainly in the section below rather than left implicit.

## Architecture (Current State)

```
Pi 5 (192.168.50.1)
 │
 ├── Backend API (bare-metal)        ── port 5000 (REST)
 │                                    ── port 5001 (WebSocket)
 │     /api/detections   /api/cluster/nodes   /api/stats
 │     /api/alerts       /api/preprocess      /api/frame
 │     /api/stream       /api/workers
 │
 ├── MinIO Object Storage (bare-metal) ── port 9000 (API)
 │     bucket: detections               ── port 9001 (Console)
 │     auto-cleanup: keep newest 100
 │
 └── k3s Kubernetes                    ── port 30080 (Frontend NodePort)
       └── frontend Deployment (containerized, Dockerfile → k3s ctr import)
```

The Pi 3 workers (`pi3-1` … `pi3-7`) are used elsewhere in the project for MPI/HPL benchmarking (Tasks 2–4) and distributed OpenCV preprocessing (Task 6). In this backend, they appear only as **SSH targets polled for health stats** — they do not host the backend itself and provide no redundancy for it.

---

## Component 1 — MinIO Object Storage

**What it is:** an open-source, S3-compatible object storage system. It exposes the same API as Amazon S3 but runs on-premise — in our case, on Pi 5's NVMe SSD.

**Why MinIO, and not the alternatives:**

| Alternative | Why not |
|---|---|
| Local filesystem | Not accessible from the dashboard as a URL |
| Amazon S3 | Requires internet access and costs money |
| PostgreSQL BLOB | Not designed for binary/image files |
| NFS | No HTTP URL for images |

MinIO gives the project HTTP URLs for images, S3 API compatibility, a web console, and fast local storage on the NVMe SSD.

**Installation:**
```bash
wget -q https://dl.min.io/server/minio/release/linux-arm64/minio
chmod +x minio
sudo mv minio /usr/local/bin/
```

**Starting MinIO:**
```bash
MINIO_ROOT_USER=<minio-user> \
MINIO_ROOT_PASSWORD=<minio-password> \
minio server /mnt/nvme/minio-data \
  --console-address ":9001" \
  --address ":9000" \
  > /mnt/nvme/logs/minio.log 2>&1 &
```

**Bucket setup:**
```bash
mc alias set myminio http://192.168.50.1:9000 <minio-user> <minio-password>
mc mb myminio/detections
mc anonymous set download myminio/detections
```

| What | Address |
|---|---|
| API | `http://192.168.50.1:9000` |
| Console | `http://192.168.50.1:9001` (credentials via environment variables) |
| Image URL format | `http://192.168.50.1:9000/detections/detection_N.jpg` |

**Auto-cleanup:** a background job runs every 5 minutes and deletes the oldest images once the bucket holds more than 100, to keep the NVMe from filling up:

```js
async function cleanupMinIO() {
  const objects = [];
  const stream = minioClient.listObjects('detections', '', true);
  stream.on('data', obj => objects.push(obj));
  stream.on('end', async () => {
    if (objects.length > 100) {
      objects.sort((a, b) => new Date(a.lastModified) - new Date(b.lastModified));
      const toDelete = objects.slice(0, objects.length - 100);
      for (const obj of toDelete) await minioClient.removeObject('detections', obj.name);
    }
  });
}
setInterval(cleanupMinIO, 5 * 60 * 1000);
```

**Current placement:** MinIO satisfies the storage-service requirement (it is explicitly named as an acceptable option in the spec), but it runs bare-metal on Pi 5 alongside the backend rather than as part of a multi-node cluster — see [Deployment Status](#deployment-status).

---

## Component 2 — Node.js Backend API

**Why Node.js:** the backend needs to simultaneously hold open WebSocket connections, SSH into 8 Pi nodes, upload to MinIO, and answer REST requests — Node's async, non-blocking I/O model fits that combination well without one slow operation blocking another.

**Dependencies** (`package.json`):
```json
{
  "dependencies": {
    "cors": "^2.8.6",
    "dotenv": "^17.4.2",
    "express": "^5.2.1",
    "minio": "^8.0.7",
    "node-ssh": "^13.2.1",
    "pg": "^8.22.0",
    "ws": "^8.21.1"
  }
}
```

> **Note:** `pg` (PostgreSQL) is listed as a dependency but is not used by this backend — `server.js` stores all detection state in memory. A separate, independently-built Postgres-backed backend (`services/backend/server.js`, port 3000) exists in the repository but is not wired into the live system; the frontend and Telegram bot both talk to this Node.js/in-memory backend on port 5000.

**Starting the backend:**
```bash
# Kill any old instance
pkill -f "node.*server.js" 2>/dev/null || true
sleep 1

cd ~/cluster/services/backend
node src/server.js > /mnt/nvme/logs/backend.log 2>&1 &

# Verify
curl -s http://192.168.50.1:5000/health
# {"status":"ok","timestamp":"..."}
```

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/detections` | Receive a detection from the Hailo inference pipeline, save its image to MinIO, broadcast over WebSocket |
| GET | `/api/detections` | Last 10 detections |
| GET | `/api/detections/latest` | Most recent detection |
| GET | `/api/cluster/nodes` | Live SSH health check (CPU/RAM/temp/uptime) of all 8 nodes, queried in parallel |
| GET | `/api/stats` | Summary counters for the dashboard |
| GET | `/api/alerts` | Recent threat alerts (polled by the Telegram bot) |
| POST | `/api/preprocess` | Distribute a frame to the Pi 3 workers for parallel OpenCV preprocessing |
| POST/GET | `/api/frame` | Latest raw camera frame (fallback path to ZeroMQ) |
| GET | `/api/stream` | MJPEG live video stream |
| POST/GET | `/api/workers` | Active Pi 3 worker list, used by the auto-scaler |
| GET | `/health` | Health check |

**Node health check, in parallel across all 8 nodes:**
```js
async function getNodeStats(node) {
  const ssh = new NodeSSH();
  await ssh.connect({ host: node.ip, username: SSH_USER_MAP[node.name], password: SSH_PASSWORD, readyTimeout: 5000 });
  const [cpu, ram, temp, uptime] = await Promise.all([
    ssh.execCommand("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"),
    ssh.execCommand("free | grep Mem | awk '{print $3/$2 * 100.0}'"),
    ssh.execCommand("cat /sys/class/thermal/thermal_zone0/temp"),
    ssh.execCommand("uptime -p")
  ]);
  ssh.dispose();
  return { name: node.name, status: 'Ready', cpu_percent, memory_percent, temperature, uptime };
}
// GET /api/cluster/nodes queries all 8 nodes with Promise.all() —
// one slow or unreachable node never blocks the other seven.
```

**WebSocket (port 5001):** a separate server pushes live updates the instant a detection or frame arrives, rather than waiting on the frontend's next poll:
```js
const wss = new WebSocket.Server({ port: 5001 });
function broadcast(data) {
  const msg = JSON.stringify(data);
  wss.clients.forEach(c => { if (c.readyState === WebSocket.OPEN) c.send(msg); });
}
```

---

## Component 3 — k3s Kubernetes

**What it is:** a lightweight Kubernetes distribution built for edge/IoT hardware — roughly 512MB RAM versus 2GB+ for full Kubernetes.

**Where it's actually used in this project:** the **frontend only** (see Task 8). `sudo kubectl get nodes` confirms a single node in the cluster:
```
NAME         STATUS   ROLES           AGE
raspberrypi  Ready    control-plane   ...
```

**Frontend deployment pipeline** (for reference — this part is fully implemented):
```bash
cd ~/cluster/services/frontend
npm run build
sudo docker build -t frontend:latest .
sudo docker save frontend:latest | sudo k3s ctr images import -
sudo kubectl create deployment frontend --image=frontend:latest
sudo kubectl expose deployment frontend --type=NodePort --port=80 --target-port=80
sudo kubectl patch service frontend -p '{"spec":{"ports":[{"port":80,"targetPort":80,"nodePort":30080}]}}'
```

### Deployment Status

**The backend is not currently deployed on k3s.** This is being actively worked on, not abandoned:

- The plan is to containerize the backend the same way the frontend is (Dockerfile → k3s ctr import → Deployment), and to solve SSH access to the worker nodes from inside a pod — most likely via a Kubernetes `Secret` holding the SSH key, mounted read-only into the pod.
- An attempt is in progress. It has not yet produced a deployment stable enough to switch over from the working bare-metal version, and the team is continuing to diagnose the exact blocker.
- Until resolved, the backend runs directly on Pi 5 (`node src/server.js`) so the live system stays stable for testing and demonstration.

**Auto-scaler** (independent of the k3s question above): a Python script (`scripts/auto_scaler.py`) watches cluster CPU via the Prometheus API and adjusts how many Pi 3 workers are active for preprocessing:
```python
SCALE_OUT_THRESHOLD = 70   # add a worker above this CPU%
SCALE_IN_THRESHOLD = 30    # remove a worker below this CPU%
MIN_WORKERS, MAX_WORKERS = 2, 7
```
Scale events post a Telegram notification, e.g. *"⬆️ AUTO SCALE OUT — Added: pi3-5 — Active workers: 5/7."*

---

## Known Limitations

- Single point of failure — backend, MinIO, and k3s control plane all run on Pi 5.
- Backend not yet on k3s (see [Deployment Status](#deployment-status)).
- Pi 3 nodes are polled for stats only, not hosting the backend or providing HA.
- No authentication on API endpoints (mitigated by private LAN isolation).

## Key Takeaways

- MinIO solves the one problem it needs to: giving detection images a plain HTTP URL that a filesystem path or database BLOB can't provide on their own.
- The backend's functional requirements — managing sensor nodes and collected data via a REST + WebSocket API — are fully met; SSH-based parallel node polling and MinIO integration both work correctly in the live system.
- The backend's deployment architecture does not yet match the assignment's k3s/HA-cluster requirement. This is a known, in-progress gap rather than an oversight, and is documented here rather than left for discovery.

---

*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Group 8*
