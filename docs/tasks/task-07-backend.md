Task 7 — Backend, Kubernetes & MinIO
!!! abstract "At a Glance" Objective: Build the backend infrastructure that ties the whole edge-computing pipeline together — a REST + WebSocket API, S3-compatible object storage for detection images, and a managed Kubernetes deployment for the frontend.

**Methodology:** Node.js/Express serves REST endpoints and a separate WebSocket server for live push updates; MinIO stores detection images with plain HTTP URLs; k3s runs the frontend as an auto-restarting, declaratively-managed container, while the backend itself runs bare-metal on Pi 5 for direct SSH access to worker nodes.

**Tools & Stack:** Node.js 20, Express, `ws`, MinIO, k3s, Docker (image build only, not runtime), `node-ssh`.

**Key Result:** 10 REST endpoints plus a WebSocket channel, all running concurrently on Pi 5 without blocking each other; frontend deployed on k3s with auto-restart and rolling updates; a CPU-driven auto-scaler dynamically adjusts active worker count.
Overview
Task 7 covers the backend infrastructure that ties the whole edge-computing pipeline together: a Node.js + Express REST API with a WebSocket server for live push updates, MinIO S3-compatible object storage for detection images, and k3s (lightweight Kubernetes) for running the frontend as a managed, auto-restarting container. All three pieces run on Pi 5.

Architecture
Internet / Local Network │ Pi 5 (192.168.50.1) │ ┌────┴───────────────────────────────────┐ │ │ Backend API MinIO Object Storage port 5000 (REST) port 9000 (API) port 5001 (WS) port 9001 (Console) │ │ ├── /api/detections bucket: detections ├── /api/cluster/nodes auto-cleanup: keep newest 100 ├── /api/stats ├── /api/alerts ├── /api/preprocess ├── /api/frame ├── /api/stream └── /api/workers │ k3s Kubernetes port 30080 (Frontend NodePort)

Component 1 — MinIO Object Storage
MinIO is an open-source, S3-compatible object storage system — it speaks the same API as Amazon S3 but runs on-premise, on Pi 5's own NVMe SSD. It's used to store every detection image so the frontend and Telegram bot can display them via a plain HTTP URL.

Why MinIO?
Alternative	Why it was not used
Local filesystem	Not accessible from a browser as a URL
Amazon S3	Requires internet access and costs money
PostgreSQL BLOB	Not designed for binary/image files
NFS	No HTTP URL for images
MinIO gives the project what none of the alternatives do together: HTTP URLs for images, S3 API compatibility (an industry standard), a web console for management, and it runs fast because it's on Pi 5's NVMe SSD rather than an SD card.

Installation
bash wget -q https://dl.min.io/server/minio/release/linux-arm64/minio chmod +x minio sudo mv minio /usr/local/bin/

Starting MinIO
```bash MINIO_ROOT_USER=admin \ MINIO_ROOT_PASSWORD=admin123 \ minio server /mnt/nvme/minio-data \ --console-address ":9001" \ --address ":9000" \

/mnt/nvme/logs/minio.log 2>&1 & ```

Create Public Bucket
```bash

Using the MinIO Client (mc)
mc alias set myminio http://192.168.50.1:9000 admin admin123 mc mb myminio/detections mc anonymous set download myminio/detections ```

Access
What	Address
API	http://192.168.50.1:9000
Console	http://192.168.50.1:9001 (admin / admin123)
Image URL format	http://192.168.50.1:9000/detections/detection_N.jpg
Component 2 — Node.js Backend API
Why Node.js?
Feature	Node.js	Python Flask	Go
SSH library	node-ssh	paramiko	—
WebSocket	ws (native)	socketio	—
MinIO client	minio (npm)	minio-py	—
Performance	High (async)	Medium	Very high
Team familiarity	Yes	Yes	No
Node.js's async, non-blocking I/O model fits the workload well — the backend needs to simultaneously hold open WebSocket connections, SSH into 8 Pi nodes, upload to MinIO, and answer REST requests, all without one slow operation blocking the others.

Installation
```bash

Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - sudo apt-get install -y nodejs

Install dependencies
cd ~/cluster/services/backend npm install ```

json // package.json { "name": "group8-backend", "version": "1.0.0", "dependencies": { "cors": "^2.8.5", "express": "^4.18.2", "minio": "^7.1.3", "node-ssh": "^13.1.0", "ws": "^8.16.0" } }

Starting the Backend
```bash

Kill any old instances
sudo kubectl scale deployment backend --replicas=0 2>/dev/null || true pkill -f "node.*server.js" 2>/dev/null || true sleep 1

cd ~/cluster/services/backend node src/server.js > /mnt/nvme/logs/backend.log 2>&1 &

Verify
curl -s http://192.168.50.1:5000/health

Output: {"status":"ok","timestamp":"..."}
```

The backend is started directly from src/server.js, not through Kubernetes — it runs bare-metal on Pi 5 because SSHing into the Pi 3 workers from inside a container would need SSH keys mounted into the container and extra permission configuration, which the team decided wasn't worth the complexity.

API Endpoints
POST /api/detections
Receives a detection event from the Hailo inference receiver.

bash curl -X POST http://192.168.50.1:5000/api/detections \ -H "Content-Type: application/json" \ -d '{ "type": "threat", "threat": true, "confidence": 0.92, "count": 1, "location": "Zone A", "classes": ["knife"], "image_base64": "..." }'

What happens internally, in order:

Saves the image to MinIO and gets back a public URL
Stores the detection in memory (keeps the last 100)
Broadcasts the new detection to every connected WebSocket client
Returns {"success": true, "id": 42}
GET /api/detections and GET /api/detections/latest
Returns the last 10 detections, or just the single most recent one:

bash curl -s http://192.168.50.1:5000/api/detections | python3 -m json.tool curl -s http://192.168.50.1:5000/api/detections/latest | python3 -m json.tool

GET /api/cluster/nodes
SSHs into all 8 nodes and returns live CPU, RAM, temperature, and uptime for each:

```js async function getNodeStats(node) { const ssh = new NodeSSH(); await ssh.connect({ host: node.ip, username: SSH_USER_MAP[node.name], password: '1234', readyTimeout: 5000 });

const [cpu, ram, temp, uptime] = await Promise.all([ ssh.execCommand("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"), ssh.execCommand("free | grep Mem | awk '{print $3/$2 * 100.0}'"), ssh.execCommand("cat /sys/class/thermal/thermal_zone0/temp"), ssh.execCommand("uptime -p") ]);

ssh.dispose(); return { name, status: 'Ready', cpu_percent, memory_percent, temperature, uptime }; } ```

All 8 nodes are queried in parallel with Promise.all(), rather than one after another, so one slow or unreachable node doesn't hold up the other seven.

GET /api/stats
Returns summary statistics for the dashboard header cards:

json { "total_detections_today": 42, "total_people_detected": 38, "total_threats_detected": 4, "detection_accuracy": 94.5, "active_nodes": 7, "total_nodes": 7 }

GET /api/alerts
Returns recent threat detections, used by the Telegram bot's polling:

json { "alerts": [ { "id": 42, "timestamp": "2026-08-23T...", "severity": "high", "message": "knife detected at Zone A", "acknowledged": false, "image_url": "http://192.168.50.1:9000/detections/detection_42.jpg" } ] }

POST /api/preprocess
Triggers distributed image preprocessing across the Pi 3 workers:

bash curl -X POST http://192.168.50.1:5000/api/preprocess \ -H "Content-Type: application/json" \ -d '{"image_base64": "..."}'

Saves the incoming frame to /tmp/frame_in_TIMESTAMP.jpg
Calls parallel_preprocess.py via exec()
Returns the preprocessed image back as base64
POST / GET /api/frame
An alternative path for Pi 4 to hand off frames (instead of ZeroMQ):

```bash

Pi 4 sends a frame
curl -X POST http://192.168.50.1:5000/api/frame -d '{"image_base64": "..."}'

Pi 5 reads the latest frame
curl -s http://192.168.50.1:5000/api/frame | python3 -m json.tool | grep ts ```

GET /api/stream
An MJPEG stream — sends frames as a multipart HTTP response, viewable directly in a browser or VLC:

js app.get('/api/stream', (req, res) => { res.setHeader('Content-Type', 'multipart/x-mixed-replace; boundary=frame'); const interval = setInterval(() => { if (!latestFrame) return; const buf = Buffer.from(latestFrame, 'base64'); res.write('--frame\r\n'); res.write('Content-Type: image/jpeg\r\n\r\n'); res.write(buf); res.write('\r\n'); }, 100); // 10 FPS stream req.on('close', () => clearInterval(interval)); });

POST / GET /api/workers
Holds the dynamic worker list used by the auto-scaler:

```bash

Auto-scaler updates the active worker list
curl -X POST http://192.168.50.1:5000/api/workers \ -d '{"workers": [{"ip":"192.168.50.91","name":"pi3-1","user":"pi3-1"}]}'

parallel_preprocess.py reads the current workers
curl -s http://192.168.50.1:5000/api/workers ```

Endpoint Summary
Method	Endpoint	Purpose
POST	/api/detections	Receive a detection from the Hailo pipeline
GET	/api/detections	Last 10 detections
GET	/api/detections/latest	Most recent detection
GET	/api/cluster/nodes	Live SSH health check of all 8 nodes
GET	/api/stats	Summary statistics
GET	/api/alerts	Recent threat alerts (Telegram bot polls this)
POST	/api/preprocess	Distributed image preprocessing
POST/GET	/api/frame	Latest raw camera frame
GET	/api/stream	MJPEG live video stream
POST/GET	/api/workers	Active Pi 3 worker list for auto-scaling
WebSocket (Port 5001)
Separate from the REST API, the backend also runs a WebSocket server that pushes live updates to any connected browser the instant something happens, instead of waiting for the frontend's next poll.

```js const wss = new WebSocket.Server({ port: 5001 });

function broadcastFrame(frame) { wss.clients.forEach(client => { if (client.readyState === WebSocket.OPEN) { client.send(JSON.stringify({ type: 'frame', frame })); } }); }

function broadcastDetection(detection) { wss.clients.forEach(client => { if (client.readyState === WebSocket.OPEN) { client.send(JSON.stringify({ type: 'detection', data: detection })); } }); } ```

How the frontend connects to it:

js const ws = new WebSocket('ws://192.168.50.1:5001'); ws.onmessage = (e) => { const msg = JSON.parse(e.data); if (msg.type === 'frame') setLiveFrame(msg.frame); if (msg.type === 'detection') setLiveDetection(msg.data); };

MinIO Auto-Cleanup
Detection images accumulate quickly, so a background job keeps the NVMe SSD from filling up by deleting the oldest images once the bucket holds more than 100:

```js async function cleanupMinIO() { const objects = []; const stream = minioClient.listObjects('detections', '', true); stream.on('data', obj => objects.push(obj)); stream.on('end', async () => { if (objects.length > 100) { objects.sort((a, b) => new Date(a.lastModified) - new Date(b.lastModified)); const toDelete = objects.slice(0, objects.length - 100); for (const obj of toDelete) { await minioClient.removeObject('detections', obj.name); } } }); }

setInterval(cleanupMinIO, 5 * 60 * 1000); // every 5 minutes ```

Component 3 — k3s Kubernetes
k3s is a lightweight Kubernetes distribution built for edge computing and IoT — it needs only about 512MB RAM, compared to 2GB+ for a full Kubernetes install, which matters on a Pi 5 that's also running MinIO and the backend.

Why Kubernetes?
Feature	Manual Docker	Kubernetes (k3s)
Auto-restart if crashed	No	Yes
Rolling updates	No	Yes
Health checks	No	Yes
Load balancing	No	Yes
Declarative config	No	Yes
Installation
```bash

Install k3s on Pi 5 (master)
curl -sfL https://get.k3s.io | sh -

Fix cgroup memory (required for Pi 5)
sudo sed -i 's/$/ cgroup_memory=1 cgroup_enable=memory/' \ /boot/firmware/cmdline.txt sudo reboot

Verify
sudo kubectl get nodes

NAME STATUS ROLES AGE
raspberrypi Ready control-plane ...
```

Deploying the Frontend
Build the Docker image:

```dockerfile

Dockerfile (services/frontend/Dockerfile)
FROM nginx:alpine COPY dist/ /usr/share/nginx/html/ EXPOSE 80 ```

```bash cd ~/cluster/services/frontend

Build the React app
npm install npm run build

Build the Docker image
sudo docker build -t frontend:latest .

Import to k3s (k3s uses containerd, not the Docker daemon)
sudo docker save frontend:latest | sudo k3s ctr images import - ```

Create the Deployment
bash sudo kubectl create deployment frontend --image=frontend:latest sudo kubectl patch deployment frontend \ -p '{"spec":{"template":{"spec":{"containers":[{"name":"frontend","imagePullPolicy":"Never"}]}}}}'

Expose as NodePort
```bash sudo kubectl expose deployment frontend --type=NodePort --port=80 --target-port=80

Force port 30080
sudo kubectl patch service frontend \ -p '{"spec":{"ports":[{"port":80,"targetPort":80,"nodePort":30080}]}}'

Verify
sudo kubectl get services

NAME TYPE CLUSTER-IP PORT(S)
frontend NodePort 10.43.x.x 80:30080/TCP
```

Redeploying After Code Changes
```bash cd ~/cluster/services/frontend

Set the correct API URL
echo "VITE_API_URL=http://192.168.50.1:5000" > .env

Rebuild and redeploy
npm run build sudo docker build -t frontend:latest . sudo docker save frontend:latest | sudo k3s ctr images import - sudo kubectl rollout restart deployment/frontend

Watch the rollout
sudo kubectl rollout status deployment/frontend ```

Useful kubectl Commands
```bash

See all pods
sudo kubectl get pods

See pod logs
sudo kubectl logs -f deployment/frontend

Describe pod (debugging)
sudo kubectl describe pod

Scale a deployment
sudo kubectl scale deployment frontend --replicas=0 # stop sudo kubectl scale deployment frontend --replicas=1 # start

Delete everything and recreate
sudo kubectl delete deployment frontend sudo kubectl delete service frontend ```

Auto-Scaler (Pi 3 Worker Auto-Scaling)
A separate Python script watches the cluster's overall CPU usage via the Prometheus API and dynamically adjusts how many Pi 3 workers are used for preprocessing — adding one when the cluster is under heavy load, removing one when it's idle.

```python

scripts/auto_scaler.py
SCALE_OUT_THRESHOLD = 70 # CPU% to add a worker SCALE_IN_THRESHOLD = 30 # CPU% to remove a worker CHECK_INTERVAL = 30 # seconds between checks MIN_WORKERS = 2 MAX_WORKERS = 7

def get_cluster_cpu(): query = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)' resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query}) return float(resp.json()['data']['result'][0]['value'][1])

while True: cpu = get_cluster_cpu() if cpu > SCALE_OUT_THRESHOLD and len(active_workers) < MAX_WORKERS: scale_out() # add a worker, notify via Telegram elif cpu < SCALE_IN_THRESHOLD and len(active_workers) > MIN_WORKERS: scale_in() # remove a worker, notify via Telegram time.sleep(CHECK_INTERVAL) ```

Scale events also send a Telegram message so the team gets a live notification, e.g. "AUTO SCALE OUT — High CPU detected! Added: pi3-5 (192.168.50.95) — Active workers: 5/7".

Troubleshooting
Problem	Fix
Backend port already in use	sudo pkill -f "node server.js"; sudo kubectl scale deployment backend --replicas=0; sleep 2; node ~/cluster/services/backend/src/server.js &
Frontend not updating after a code change	npm run build; sudo docker build -t frontend:latest .; sudo docker save frontend:latest \| sudo k3s ctr images import -; sudo kubectl rollout restart deployment/frontend
MinIO not accessible	pgrep -f "minio server" to check it's running; if not, restart it with the same MINIO_ROOT_USER/PASSWORD env vars as before
Pod stuck in ImagePullBackOff	The image wasn't imported properly — re-run docker save \| k3s ctr images import, then restart the deployment
Note: A Second, Parallel Backend Exists
This document describes src/server.js — the in-memory + SSH + MinIO + WebSocket backend on port 5000, confirmed as the one actually used in production: the frontend's VITE_API_URL and the Telegram bot's BACKEND_URL both default to this address.

The repository also contains a second, independently-built backend at services/backend/server.js (port 3000) that stores data in a real PostgreSQL database instead of memory, documented separately under Task 7's database work. It was developed and tested against a database running on a team member's laptop rather than on Pi 5, and nothing in the frontend or Telegram bot is configured to talk to port 3000 — so it works standalone but isn't wired into the live system this document describes. Worth keeping in mind so the two aren't confused when reading the wider codebase.

Key Takeaways
MinIO solves exactly one problem well: giving detection images a plain HTTP URL the browser can load, which a filesystem path or a database BLOB can't do on their own.
Node's async model matches the workload. SSH to 8 nodes, MinIO uploads, WebSocket pushes, and REST requests all happen concurrently without one blocking another — the Promise.all() pattern in getNodeStats is the clearest example of this.
The backend runs bare-metal, the frontend runs in k3s. A deliberate, documented trade-off: SSH key management inside a container wasn't worth the complexity for a student-timeline project.
k3s buys reliability, not raw performance — auto-restart, rolling updates, and health checks that a plain docker run doesn't give you, at roughly a quarter of the RAM cost of full Kubernetes.
Two feedback loops keep the system self-maintaining: MinIO's 5-minute cleanup job bounds disk usage, and the CPU-based auto-scaler bounds how many workers are active — both running unattended in the background.
Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Group 8