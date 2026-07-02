# Cloud Computing SS2026 — Team Progress Report

## Frankfurt University of Applied Sciences

## Prof. Dr. Christian Baun

---

## Team Members

| Member   | Role                                                                |
| -------  | ------------------------------------------------------------------- |
| Janak    | Infrastructure Lead (PXE Boot, MPI, Kubernetes, Distributed System) |
| Purvesh  | Backend Developer (Node.js API)                                     |
| Disha    | Object Detection (YOLO Model Training)                              |
| Marcos   | Telegram Bot                                                        |
| Disha    | Frontend Developer (React Dashboard)                                |
| Shubhangi| Detection Service and Backend Integration                           |


---

## Task 1 — PXE Boot and Network Boot Infrastructure

**Approach and Solution:**
Our goal was to boot all Raspberry Pi 3B worker nodes entirely over the network without any operating system on their SD cards. We set up the Raspberry Pi 5 as the master node acting as DHCP, TFTP, and NFS server simultaneously. The NVMe SSD (WD Black SN7100, 500GB) was mounted at /mnt/nvme to serve as fast storage for both TFTP boot files and NFS root filesystems.

We downloaded the 32-bit Raspberry Pi OS Lite (Bookworm) image, mounted it using loop devices, and copied the boot partition to the TFTP root and the root filesystem to the NFS export directory. We configured dnsmasq to assign static IP addresses based on MAC addresses, ensuring each Pi 3 always receives the same IP at every boot. Each Pi 3 was given its own separate NFS root directory (pi3-1 through pi3-7) with a unique hostname set in /etc/hostname, so each worker node has a distinct identity on the cluster.

**Problems Faced:**

The first major challenge was the MAC address-based TFTP directory naming. The Pi 3 bootloader looks for files in a directory named after the last 8 hex digits of its MAC address. We initially calculated these directory names incorrectly, which caused several nodes to fall back to the default cmdline.txt — which pointed to a non-existent NFS path — and fail to boot. After careful analysis of dnsmasq TFTP logs, we identified the exact directory names each Pi 3 was requesting and recreated them correctly.

A second significant challenge was the 32-bit versus 64-bit architecture mismatch. Pi 5 runs 64-bit (aarch64) while Pi 3 runs 32-bit ARM (armhf). When we attempted to use chroot from Pi 5 into the Pi 3 NFS root to configure it, every command failed with ELF format errors because the Pi 5 cannot execute 32-bit ARM binaries natively. We attempted to use QEMU user-mode emulation as a workaround but found it too complex for our setup. The solution was to boot one Pi 3 first, SSH into it, and configure the shared NFS root from the Pi 3 itself — since it runs the correct architecture.

A third ongoing challenge was that two Pi 3 nodes (pi3-2 and pi3-3) consistently failed to boot despite having correct MAC address directories with all required files. Their ethernet ports show link lights but they send no DHCP packets at all. We verified the TFTP directories, cmdline.txt contents, and NFS exports — all were correct. The root cause appears to be a hardware issue specific to those two boards, possibly related to their OTP network boot fuse configuration. We were unable to resolve this within the project timeframe and proceeded with the remaining 5 operational worker nodes.

We also tried to use 64-bit Raspberry Pi OS on the Pi 3B nodes (since the CPU supports it) hoping for better performance. However, when we copied the 64-bit Pi 5 NFS root for use by Pi 3 nodes, many Pi 3s failed to boot reliably. The 64-bit kernel requires more RAM and places higher load on the Pi 3B hardware, causing instability especially when multiple nodes boot simultaneously. We reverted to the 32-bit OS which is stable and reliable on Pi 3B hardware.

Another recurring problem was the Pi 5 eth0 interface losing its static IP address (192.168.50.1) after system restarts or network service restarts. This caused all Pi 3 DHCP requests to fail with "DHCP packet received on eth0 which has no address" errors. This was resolved permanently by configuring NetworkManager with nmcli to set a permanent static IP on the ethernet interface.

**Current Status:** COMPLETE. 5 out of 7 Raspberry Pi 3B worker nodes boot successfully via PXE over the network (pi3-1, pi3-4, pi3-5, pi3-6, pi3-7). Each has a unique hostname and individual NFS root filesystem served from the Pi 5 NVMe SSD. 2 nodes (pi3-2, pi3-3) remain non-functional due to suspected hardware issues.

**Lead:** Janak

---

## Task 2 — HPL Benchmark (GFLOPS Measurement)

**Approach and Solution:**
We installed the HPCC (HPC Challenge) benchmark suite on the Pi 3 worker nodes to measure floating point performance. Since all Pi 3s initially shared a single NFS root, installing once propagated to all nodes automatically. We configured hpccinf.txt with appropriate matrix sizes for both single-node and multi-node runs.

The main challenge was internet connectivity on Pi 3 nodes for package installation. The Pi 3B WiFi does not support 5GHz networks and the cluster ethernet interface was isolated from the internet. We solved this by connecting each Pi 3 to a mobile hotspot via its built-in WiFi for installation, while removing the ethernet default route to keep cluster traffic on the 192.168.50.0/24 network. We also encountered 404 errors for several packages from the Raspbian repository (outdated package versions), which we resolved using the --fix-missing apt flag.

We ran HPL benchmarks in two configurations. Single node (N=1000, P=1, Q=1) achieved 1.385 GFlops. The 6-node cluster (N=5000, P=1, Q=6) achieved 1.208 GFlops. The cluster result being lower than single node directly demonstrates the communication overhead cost for small problem sizes — a preview of Amdahl's Law.

**Current Status:** COMPLETE. Single node: 1.385 GFlops. 6-node cluster: 1.208 GFlops. All tests passed residual checks.

**Lead:** Janak

---

## Task 3 — MPI Cluster Setup

**Approach and Solution:**
We installed OpenMPI 4.1.4 on all Pi 3 worker nodes and configured passwordless SSH between nodes to enable MPI job distribution. A hostfile listing all Pi 3 IP addresses was created for use with mpirun.

**Important Limitation — MPI Only Works Between Pi 3 Worker Nodes:**
A critical limitation we discovered is that MPI jobs cannot be launched from the Pi 5 master node targeting Pi 3 worker nodes. Pi 5 runs 64-bit Debian and had OpenMPI 5.x (later switched to MPICH 4.2.1) while Pi 3 nodes run 32-bit Raspbian with OpenMPI 4.1.4 / MPICH 4.0.2. These versions are incompatible at the process manager level — Pi 5's mpirun uses PRTE (prun execution environment) while Pi 3 uses Hydra. Every attempt to run mpirun from Pi 5 resulted in "PRTE has lost communication with remote daemon" errors because Pi 3 could not find /usr/bin/prted.

We tried multiple approaches to resolve this: switching Pi 5 to MPICH (same implementation as Pi 3), using explicit launcher flags, trying the fork launcher, and specifying the hydra_pmi_proxy path explicitly. None of these fully resolved the incompatibility because even with MPICH on both sides, the minor version difference (4.2.1 vs 4.0.2) caused protocol mismatches in the hydra proxy daemon.

The working solution is to run mpirun from pi3-1 (a worker node) and target the other Pi 3 worker nodes. In this configuration, MPI jobs work correctly across all Pi 3 nodes since they all run the same OpenMPI version. Pi 5 acts as the SSH gateway and coordinator but does not participate directly as an MPI process.

We successfully verified that `hostname` and `hpcc` run correctly across all 5 Pi 3 nodes when launched from pi3-1. For future improvement, installing the same exact MPI version on both Pi 5 and all Pi 3 nodes (compiled from source if necessary) would resolve this limitation and allow Pi 5 to act as the true MPI master.

**Current Status:** COMPLETE (with limitation). MPI works between Pi 3 worker nodes only. Pi 5 cannot directly participate as MPI master due to version incompatibility. MPI jobs run from pi3-1 across pi3-1, pi3-4, pi3-5, pi3-6, pi3-7 successfully.

**Lead:** Janak

---

## Task 4 — Amdahl's Law and Gustafson's Law

**Approach and Solution:**
We plan to demonstrate both laws empirically using HPL benchmark results across different node counts (1, 2, 3, 4, 5, 6 nodes) and our distributed image preprocessing pipeline. For Amdahl's Law, we measure speedup as we increase the number of worker nodes and compare against the theoretical prediction. For Gustafson's Law, we scale the problem size proportionally with nodes and measure sustained performance.

We already have concrete data from our preprocessing pipeline. Running image preprocessing on Pi 5 alone takes 0.591 seconds. Distributing the same task across 4 Pi 3 workers in parallel takes approximately 15-25 seconds due to SSH connection and SCP file transfer overhead. This demonstrates that for small workloads, communication overhead dominates over computation — exactly what Amdahl's Law predicts. The serial fraction in our system is the SSH handshake and data transfer time.

**Current Status:** IN PROGRESS. HPL data for 1 and 6 nodes collected. Full Amdahl's Law graph with all node counts still pending.

**Lead:** Janak

---

## Task 5 — Monitoring with Prometheus and Grafana

**Approach and Solution:**
We plan to deploy Prometheus and Grafana on the Kubernetes cluster. node_exporter will be installed on all Pi 3 workers to expose metrics. Prometheus scrapes these endpoints and Grafana visualizes them in live dashboards.

**Current Status:** PLANNED. Kubernetes cluster is ready. node_exporter not yet deployed.

**Lead:** -

---

## Task 6 — Object Detection Model Training and Deployment

**Approach and Solution:**
We trained a custom YOLOv8 model using Google Colab with a dataset prepared via Roboflow covering 20 object classes. Two training iterations were performed — baseline on 28 May 2026 and an improved version on 08 June 2026 after dataset expansion. The trained model was deployed on Raspberry Pi 4 with an IMX708 wide-angle camera. The detection script captures frames continuously, runs YOLO inference, and sends results including a base64-encoded image to the backend API every 2 seconds. The script runs headlessly with no display required.

**Current Status:** COMPLETE. YOLO model running live on Pi 4, detecting and reporting objects in real time.

**Lead:** Disha

---

## Task 7 (Part A) — Backend and Distributed Storage

**Approach and Solution:**
We built a Node.js REST API using Express with 7 endpoints: POST /api/detections (receive from Pi 4), GET /api/detections (list), GET /api/detections/latest, GET /api/cluster/nodes (SSH to get live stats), GET /api/stats, GET /api/alerts, and POST /api/preprocess (trigger Pi 3 preprocessing).

For distributed storage, we deployed MinIO on the Pi 5 NVMe SSD. All detection images are uploaded to MinIO and served via public S3 URLs. An automatic cleanup routine runs every 5 minutes keeping only the last 100 images to prevent storage overflow. MinIO provides S3-compatible object storage accessible from any node on the cluster network.

The backend SSHs into each Pi node on demand using node-ssh to collect CPU usage, RAM usage, temperature, and uptime — which are displayed in the frontend dashboard as live cluster metrics.

**Current Status:** COMPLETE. Backend running on Pi 5 port 5000. MinIO running on port 9000. All endpoints functional with real data from Pi 4 YOLO.

**Lead:** Janak / Purvesh

---
## Task 7 (Part B) — Detection Service and Backend Integration

**Approach and Solution:**

We developed a Python-based Detection Service using YOLOv8 to perform object detection on images captured by the Raspberry Pi sensor node. The Detection Service loads the trained YOLO model, processes input images, performs inference, and extracts detection results including detected object classes, confidence scores, object count, threat status, timestamp, and image path. The generated detection metadata is formatted as JSON and transmitted to the existing Node.js backend through the `POST /api/detections` REST API endpoint.

The Detection Service was integrated with the backend by configuring the backend environment and PostgreSQL database connection. The required PostgreSQL database and tables were created and verified before testing. End-to-end integration was validated by executing the complete workflow from Detection Service → Backend → PostgreSQL. Backend availability was verified using the `/api/health` endpoint, while SQL queries confirmed that detection records were successfully stored in the database. Complete technical documentation was prepared covering project setup, dependency installation, YOLO detection, metadata generation, backend integration, testing, and verification. All implementation code and documentation were committed and pushed to the `feature/task7b-detection-service` branch for review and integration.

**Problems Faced:**

The first major challenge was resolving Git merge conflicts in `server.js`. During backend integration, conflicting changes from multiple contributors left Git merge markers (`<<<<<<<`, `=======`, `>>>>>>>`) in the source code, preventing the backend from starting successfully. The conflicts were manually reviewed, the correct implementation was reconstructed, and the backend was tested to ensure all REST API endpoints functioned correctly.

The second challenge was setting up the Detection Service environment. Several required Python packages, including Ultralytics YOLO, OpenCV, Requests, Pillow, NumPy, and python-dotenv, were initially missing from the virtual environment. Some project files also required verification before the Detection Service could execute successfully. After installing the required dependencies and validating the project structure, the Detection Service operated correctly.

Another challenge was configuring PostgreSQL connectivity between the Detection Service and the backend. Initially, the backend failed to establish a database connection because of incorrect authentication settings and missing environment configuration. The required `.env` file was configured, the PostgreSQL database schema was initialized, backend connectivity was verified, and successful communication between the Detection Service and backend was established. End-to-end testing confirmed successful REST API communication, HTTP Status 200 responses, and correct storage of detection metadata in PostgreSQL.

**Current Status:**

**COMPLETE.** Detection Service successfully integrated with the Node.js backend. Detection metadata is transmitted through the REST API and stored in PostgreSQL. Backend health endpoint verified, end-to-end Detection Service → Backend → PostgreSQL workflow successfully tested, and complete Phase 1–5 technical documentation prepared and pushed to the `feature/task7b-detection-service` branch.

**Lead:** Shubhangi
---

## Task 7 (Part C) — Kubernetes Cluster and Distributed Preprocessing

**Approach and Solution:**
We installed k3s (lightweight Kubernetes) on Pi 5 as the control plane and joined 5 Pi 3 worker nodes. Both frontend and backend are containerized with Docker and deployed as Kubernetes Deployments with NodePort Services.

**Problems Faced:**
The primary challenge was missing cgroup memory support. k3s requires cgroup_memory=1 cgroup_enable=memory kernel parameters. On Pi 5, adding these parameters to /boot/firmware/cmdline.txt was done incorrectly in an early attempt — the file was accidentally overwritten with only the cgroup parameters, removing all original boot parameters. Pi 5 dropped to an initramfs rescue shell and could not boot normally. We recovered by mounting the boot partition from the initramfs shell and reconstructing the correct cmdline.txt from memory.

For Pi 3 nodes, the cgroup parameters were added to the TFTP cmdline.txt files served to each node via TFTP, since Pi 3s have no local storage for boot configuration.

Another challenge was that the backend Docker container cannot easily SSH to Pi 3 nodes for the preprocessing pipeline because SSH keys are not mounted inside containers. Our current solution runs the backend directly on Pi 5 (outside Kubernetes) so it has full SSH access to Pi 3 nodes, while the frontend remains cleanly deployed in Kubernetes.

For the distributed image preprocessing pipeline, Pi 5 receives frames from Pi 4, splits each frame into 4 horizontal strips, and sends each strip simultaneously to a different Pi 3 worker (pi3-1, pi3-4, pi3-5, pi3-6) via SSH. Each Pi 3 applies contrast enhancement and Gaussian blur to its strip using OpenCV, then returns the result. Pi 5 merges the 4 strips back into a complete preprocessed frame which is returned to Pi 4 for YOLO inference.

Installing OpenCV on Pi 3 nodes was a multi-step challenge. The standard python3-opencv package from the Raspbian repository had 404 errors for several dependencies. We resolved this by installing opencv-python-headless from PyPI via pip3 and piwheels (the ARM-optimized Python package mirror). Multiple missing shared libraries were then discovered one by one (libwebpdemux.so.2, libopenjp2.so.7, libavcodec.so.59, etc.) and installed individually on each node.

**Current Status:** COMPLETE (partial). k3s cluster running with 6 nodes. Frontend deployed on Kubernetes (port 30080). Backend running on Pi 5 directly (port 5000). Parallel preprocessing across 4 Pi 3 workers operational with approximately 15-20 second processing time per frame.

**Lead:** Janak

---

## Task 8 — Frontend Dashboard

**Approach and Solution:**
We built a React dashboard using Vite displaying: a statistics header bar, latest detection panel with real camera image from MinIO, alerts panel, cluster status grid with live CPU/RAM progress bars per node, and a recent detections table. All data is fetched automatically with setInterval polling. useRef is used to preserve previous data during fetch updates, eliminating flickering. The dashboard is served via Nginx inside a Docker container deployed on Kubernetes.

**Current Status:** COMPLETE. Accessible at http://192.168.50.1:30080 from any device on the cluster network.

**Lead:** DIsha / Janak

---

## Task 9 — Telegram Bot

**Approach and Solution:**
The bot will send automatic threat alerts when the YOLO model detects dangerous objects. It will poll the backend alerts endpoint every 30 seconds and send Telegram messages with detection images for unacknowledged threats. Interactive commands (/status, /latest, /alerts, /stats) will allow querying the system remotely.

**Current Status:** PLANNED. Backend alert endpoint is ready. Bot implementation not yet started.

**Lead:** Marcos

---

## Task 10 — Documentation

**Approach and Solution:**
We maintain a detailed living documentation (pi-cluster-setup.md) recording every configuration step, file path, MAC address mapping, IP assignment, and command used. The document was updated continuously throughout the project. Team blueprints have been created for each member (backend, frontend, Telegram bot) defining exact API formats, sample data, and packages to use.

**Current Status:** IN PROGRESS. Internal documentation comprehensive. GitHub documentation page being prepared.

**Lead:** All team members

---

## Summary Table

| Task | Description                            | Status                | Lead            |
| ---- | -------------------------------------- | --------------------- | --------------- |
| 1    | PXE Boot (5/7 nodes)                   | ✅ Complete           | Janak           |
| 2    | HPL Benchmark                          | ✅ Complete           | Janak           |
| 3    | MPI (Pi 3 to Pi 3 only)                | ✅ Complete (limited) | Janak           |
| 4    | Amdahl's / Gustafson's Law             | 🔄 In Progress        | Janak           |
| 5    | Monitoring (Prometheus/Grafana)        | 📋 Planned            | janak           |
| 6    | Object Detection (YOLO)                | ✅ Complete           | Disha           |
| 7A   | Backend + MinIO Storage                | ✅ Complete           | Purvesh / Janak |
| 7B   | Detection Service + Backend Integration| ✅ Complete           | Shubhangi       |
| 7C   | Kubernetes + Distributed Preprocessing | ✅ Complete (partial) | Janak           |
| 8    | Frontend Dashboard                     | ✅ Complete           | Disha / Janak   |
| 9    | Telegram Bot                           | 📋 Planned            | Marcos          |
| 10   | Documentation                          | 🔄 In Progress        | All             |

---

## Open Questions and Request for Advice

We would greatly appreciate Professor Baun's guidance on the following challenges we encountered:

**1. MPI Version Compatibility Between Pi 5 and Pi 3:**
We were unable to establish a working MPI setup where Pi 5 (64-bit, MPICH 4.2.1) acts as the master and Pi 3 nodes (32-bit, MPICH 4.0.2 / OpenMPI 4.1.4) act as workers. The version and architecture differences caused process manager incompatibilities. Would compiling the same MPI version from source on both architectures resolve this? Is there a recommended approach for mixed-architecture MPI clusters?

**2. Pi 3 Nodes Not Booting Despite Correct MAC Configuration:**
Two Pi 3 nodes (pi3-2 and pi3-3) show ethernet link lights but send no DHCP packets at all. We verified their MAC address TFTP directories have all required files and correct cmdline.txt. OTP fuses were burned for network boot on these boards. tcpdump on Pi 5 confirms zero packets from their MAC addresses. Could this be a failed OTP burn, hardware ethernet fault, or something in the SD card bootloader? We have run out of ideas to diagnose this remotely.

**3. HPL Performance on Heterogeneous Cluster (Pi 5 + Pi 3):**
Our cluster is heterogeneous — Pi 5 (aarch64, 8GB RAM) and Pi 3B (armhf, 1GB RAM). We could not include Pi 5 as an MPI worker for HPL due to the MPI version issue. Is it possible to benchmark a heterogeneous cluster meaningfully with HPL, and if so, what configuration would be recommended?

**4. Distributed Preprocessing Performance:**
Our SSH-based distributed preprocessing pipeline takes 15-25 seconds per frame, which is far too slow for real-time use. The bottleneck is SSH connection setup and SCP file transfer overhead, not the actual computation. Would a persistent MPI process on each Pi 3 (once MPI is fixed) significantly reduce this overhead? Are there better inter-process communication mechanisms suitable for our setup?

**5. 64-bit OS on Pi 3B:**
We attempted to use a 64-bit OS for Pi 3B nodes via PXE boot, hoping for better performance and eliminating the 32-bit/64-bit mismatch with Pi 5. However, some Pi 3 nodes failed to boot reliably with the 64-bit kernel, and the ones that did boot showed higher resource usage. Is 64-bit OS on Pi 3B recommended for cluster workloads, and what kernel parameters or configurations would make it stable?

---

_Submitted by the Cloud Computing SS2026 Team_
_Frankfurt University of Applied Sciences_
_Prof. Dr. Christian Baun_
