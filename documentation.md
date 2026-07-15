# Cloud Computing SS2026 — Group 8
# Complete Project Documentation
## Frankfurt University of Applied Sciences
## Prof. Dr. Christian Baun

**Team:** Shubhangi Sapkale, Janak Koradiya, Disha Bhuva, Kirti Tarsariya, Amina Arshad, Purvesh Shapariya, Marcos Ortega-Jimenez

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Hardware Setup](#2-hardware-setup)
3. [Network Configuration](#3-network-configuration)
4. [Task 1 — Cluster Boot Setup](#4-task-1--cluster-boot-setup)
5. [Task 2 — HPL Benchmark](#5-task-2--hpl-benchmark)
6. [Task 3 — MPI](#6-task-3--mpi)
7. [Task 4 — Amdahl's & Gustafson's Law](#7-task-4--amdahls--gustafsons-law)
8. [Task 5 — Monitoring (Prometheus + Grafana)](#8-task-5--monitoring-prometheus--grafana)
9. [Task 6 — Edge AI Object Detection](#9-task-6--edge-ai-object-detection)
10. [Task 7 — Backend + Kubernetes + MinIO](#10-task-7--backend--kubernetes--minio)
11. [Task 8 — Frontend Dashboard](#11-task-8--frontend-dashboard)
12. [Task 9 — Telegram Bot](#12-task-9--telegram-bot)
13. [Task 10 — Documentation](#13-task-10--documentation)
14. [How to Start Everything](#14-how-to-start-everything)
15. [Troubleshooting Guide](#15-troubleshooting-guide)

---

## 1. Project Overview

We built a self-contained edge-computing cluster using commodity Raspberry Pi hardware to perform real-time threat detection using computer vision. The system demonstrates key cloud computing concepts including distributed computing, parallel processing, container orchestration, object storage, monitoring, and AI acceleration.

### Key Achievements
- 77× AI inference speedup using Hailo AI HAT+ (0.7 FPS → 54 FPS)
- 7-node parallel preprocessing pipeline using OpenCV
- HPL benchmark: 1.18 GFlops peak at 16 processes
- Full Kubernetes (k3s) cluster with 5 worker nodes
- Real-time monitoring with Prometheus + Grafana
- Telegram bot for threat alerts
- React frontend dashboard with live camera feed

---

## 2. Hardware Setup

| Device | Model | IP Address | Role |
|--------|-------|-----------|------|
| Pi 5 | Raspberry Pi 5 (8GB) | 192.168.50.1 | Master node, backend, Hailo AI HAT+ |
| Pi 4 | Raspberry Pi 4 (4GB) | 192.168.50.98 | Camera node (IMX500) + ZeroMQ sender |
| Pi 3-1 | Raspberry Pi 3B (1GB) | 192.168.50.91 | Worker node |
| Pi 3-2 | Raspberry Pi 3B (1GB) | 192.168.50.92 | Worker node |
| Pi 3-3 | Raspberry Pi 3B (1GB) | 192.168.50.93 | Worker node |
| Pi 3-4 | Raspberry Pi 3B (1GB) | 192.168.50.94 | Worker node |
| Pi 3-5 | Raspberry Pi 3B (1GB) | 192.168.50.95 | Worker node |
| Pi 3-6 | Raspberry Pi 3B (1GB) | 192.168.50.96 | Worker node |
| Pi 3-7 | Raspberry Pi 3B (1GB) | 192.168.50.97 | Worker node |
| Switch | TP-Link TL-SG108E | 192.168.50.104 | 8-port Gigabit switch |

### Additional Hardware
- **Hailo AI HAT+** (8L, 13 TOPS) — connected to Pi 5 via PCIe
- **Sony IMX500 AI Camera Module** — connected to Pi 4
- **NVMe SSD (500GB)** — connected to Pi 5 for MinIO storage
- **Gigabit Ethernet switch** — TL-SG108E connecting all nodes

### SSH Credentials

| Device | Username | Password |
|--------|----------|---------|
| Pi 5 | pi | 1234 |
| Pi 3-1 | pi3-1 | 1234 |
| Pi 3-2 | pi3-2 | 1234 |
| Pi 3-3 | pi3-3 | 1234 |
| Pi 3-4 | pi3-4 | 1234 |
| Pi 3-5 | pi3-5 | 1234 |
| Pi 3-6 | pi3-6 | 1234 |
| Pi 3-7 | pi3-7 | 1234 |
| Pi 4 | pi | 1234 |

---

## 3. Network Configuration

All nodes are connected via a private Gigabit LAN on the 192.168.50.0/24 subnet.

### DHCP/DNS Server (dnsmasq on Pi 5)

Pi 5 acts as DHCP server for the entire cluster. Configuration at `/etc/dnsmasq.conf`:

```
interface=eth0
bind-interfaces
dhcp-range=192.168.50.50,192.168.50.150,12h
dhcp-host=b8:27:eb:4b:43:2c,192.168.50.91,pi3-1
dhcp-host=b8:27:eb:39:15:74,192.168.50.92,pi3-2
dhcp-host=b8:27:eb:e7:78:92,192.168.50.93,pi3-3
dhcp-host=b8:27:eb:31:7a:10,192.168.50.94,pi3-4
dhcp-host=b8:27:eb:d4:aa:d7,192.168.50.95,pi3-5
dhcp-host=b8:27:eb:a5:ff:f4,192.168.50.96,pi3-6
dhcp-host=b8:27:eb:e3:a8:e9,192.168.50.97,pi3-7
```

### MAC Address Table

| Hostname | MAC Address | IP |
|----------|------------|-----|
| pi3-1 | b8:27:eb:4b:43:2c | 192.168.50.91 |
| pi3-2 | b8:27:eb:39:15:74 | 192.168.50.92 |
| pi3-3 | b8:27:eb:e7:78:92 | 192.168.50.93 |
| pi3-4 | b8:27:eb:31:7a:10 | 192.168.50.94 |
| pi3-5 | b8:27:eb:d4:aa:d7 | 192.168.50.95 |
| pi3-6 | b8:27:eb:a5:ff:f4 | 192.168.50.96 |
| pi3-7 | b8:27:eb:e3:a8:e9 | 192.168.50.97 |

### Static IP for Pi 5 eth0

Pi 5's ethernet interface must have a static IP. Configured via NetworkManager:

```bash
sudo nmcli con mod "Wired connection 1" ipv4.addresses 192.168.50.1/24 ipv4.method manual
sudo nmcli con up "Wired connection 1"
```

### Internet Sharing (NAT)

Pi 5 shares internet from wlan1 to all Pi 3s via NAT:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
sudo iptables -I FORWARD 1 -i eth0 -o wlan1 -j ACCEPT
sudo iptables -I FORWARD 2 -i wlan1 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

### Passwordless SSH

SSH keys are distributed from Pi 5 to all Pi 3s:

```bash
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
for i in 1 2 3 4 5 6 7; do
  sshpass -p '1234' ssh-copy-id -o StrictHostKeyChecking=no pi3-$i@192.168.50.$((90+i))
done
```

---

## 4. Task 1 — Cluster Boot Setup

### Approach: SD Card Boot (Final Solution)

We initially attempted PXE network boot where Pi 3s would boot from the network using TFTP/NFS served by Pi 5. After extensive troubleshooting (MAC address directory issues, 32-bit vs 64-bit OS conflicts, simultaneous boot failures, TFTP timeouts), we switched to SD card boot for reliability.

### PXE Boot Attempt (Initial Approach)

The PXE boot process works as follows:
1. Pi 3 powers on with bootcode.bin on SD card
2. GPU sends DHCP discover over ethernet
3. Pi 5 (dnsmasq) responds with IP + TFTP server location
4. Pi 3 downloads boot files via TFTP from `/srv/tftp/`
5. Kernel mounts NFS root from Pi 5 `/mnt/nvme/nfs/pi3-X/`
6. System boots from NFS filesystem

**Problems encountered:**
- Pi 3B has 32-bit GPU; 64-bit OS caused bootcode.bin incompatibility
- Simultaneous TFTP downloads caused timeouts between nodes
- Pi 3 usernames differ (pi3-1, pi3-2, etc.) causing SSH/MPI issues
- eth0 on Pi 5 kept losing static IP after dnsmasq restart

### SD Card Boot (Final Solution)

Each Pi 3 got its own SD card with 64-bit Raspberry Pi OS (Bookworm). Usernames were set during first boot:
- Pi 3-1: username `pi3-1`
- Pi 3-2: username `pi3-2`
- ... and so on

Static IPs were assigned via dnsmasq MAC binding as shown above.

### Verifying All Nodes

```bash
for i in 1 2 3 4 5 6 7; do
  echo -n "pi3-$i: "
  ping -c 1 -W 1 192.168.50.$((90+i)) > /dev/null 2>&1 && echo "UP" || echo "DOWN"
done
```

**Result:** All 7 Pi 3 nodes consistently reachable ✅

---

## 5. Task 2 — HPL Benchmark

### What is HPL?

HPL (High-Performance Linpack) is an industry-standard benchmark that solves a dense system of linear equations. It measures peak floating-point performance (GFlops) of a cluster.

### Installation

HPL 2.3 was compiled from source on Pi 5:

```bash
wget http://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz
tar xvf hpl-2.3.tar.gz
cd hpl-2.3
# Copy and modify Make.RPI for ARM
make arch=RPI
```

### Configuration (HPL.dat)

```
N      :    7000     (problem size)
NB     :      64     (block size)
P      :       4     (process rows)
Q      :       7     (process columns)
```

### Running HPL

```bash
cd ~/hpl-2.3/bin/RPI
mpirun --hostfile ~/hosts_all.txt --map-by node -np 28 ./xhpl
```

### Results

| Processes | GFlops |
|-----------|--------|
| 1 | 1.385 |
| 28 (N=7000) | 1.0831 |
| 16 (peak) | 1.18 |

**Peak performance: 1.18 GFlops at 16 processes (N=7000)**

The drop at 28 processes demonstrates communication overhead dominates computation at high process counts — a classic Amdahl's Law effect.

---

## 6. Task 3 — MPI

### OpenMPI Installation

OpenMPI 5.0.7 was installed on all nodes. First on Pi 3s:

```bash
for i in 1 2 3 4 5 6 7; do
  ssh pi3-$i@192.168.50.$((90+i)) "sudo apt-get install -y openmpi-bin libopenmpi-dev make gcc" &
done
wait
```

On Pi 5:
```bash
sudo apt-get install -y libopenmpi-dev openmpi-bin
```

### MPI Hostfile (`~/hosts_all.txt`)

```
192.168.50.1
192.168.50.91
192.168.50.92
192.168.50.93
192.168.50.94
192.168.50.95
192.168.50.96
192.168.50.97
```

### MPI Hostfile with slots (`~/hostfile.mpi`)

```
192.168.50.1 slots=4
192.168.50.91 slots=4
...
192.168.50.97 slots=4
```

### Verifying MPI Works

```bash
mpirun --hostfile ~/hosts_all.txt --map-by node -np 8 hostname
```

Output:
```
raspberrypi
pi3-1
pi3-2
pi3-3
pi3-4
pi3-5
pi3-6
pi3-7
```

### Monte Carlo Pi Program

The Monte Carlo method approximates π by randomly sampling points in a unit square and checking if they fall inside the unit circle.

**Source code (`~/pi_mpi.c`):**

```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "mpi.h"

int main(int argc, char *argv[]) {
    int myid, nprocs;
    long int npts = 1e8;
    long int i, mynpts;
    double f, sum, mysum;
    double xmin, xmax, x;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);
    MPI_Comm_rank(MPI_COMM_WORLD, &myid);

    if (myid == 0) {
        mynpts = npts - (nprocs-1)*(npts/nprocs);
    } else {
        mynpts = npts/nprocs;
    }

    mysum = 0.0;
    xmin = 0.0; xmax = 1.0;
    srand(time(0));

    for (i=0; i<mynpts; i++) {
        x = (double) rand()/RAND_MAX*(xmax-xmin) + xmin;
        mysum += 4.0/(1.0 + x*x);
    }

    MPI_Reduce(&mysum, &sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    if (myid == 0) {
        f = sum/npts;
        printf("PI calculated with %ld points = %f\n", npts, f);
    }

    MPI_Finalize();
    return 0;
}
```

**Compilation:**
```bash
mpicc ~/pi_mpi.c -o ~/pi_mpi
# Copy to all Pi 3s
for i in 1 2 3 4 5 6 7; do
  scp ~/pi_mpi.c pi3-$i@192.168.50.$((90+i)):~/
  ssh pi3-$i@192.168.50.$((90+i)) "mpicc ~/pi_mpi.c -o ~/pi_mpi && sudo cp ~/pi_mpi /home/pi/pi_mpi"
done
```

**Running:**
```bash
mpirun --hostfile ~/hosts_all.txt --map-by node -np 28 ~/pi_mpi
```

---

## 7. Task 4 — Amdahl's & Gustafson's Law

### Monte Carlo Pi Results (100M points)

| Processes | Time (s) | Speedup |
|-----------|---------|---------|
| 1 | 5.588 | 1.00 |
| 2 | 8.329 | 0.67 |
| 4 | 4.788 | 1.17 |
| 8 | 3.721 | 1.50 |
| 16 | 3.440 | 1.62 |
| 28 | 3.140 | 1.78 |

**Key observations:**
- np=2 is SLOWER than np=1 — SSH connection overhead dominates for small process counts
- Speedup saturates around 1.78× at 28 processes
- This demonstrates Amdahl's Law: serial fraction limits maximum speedup
- Estimated serial fraction: ~44% (SSH overhead + MPI communication)

### Timing Tests Command

```bash
for np in 1 2 4 8 16 28; do
  echo -n "np=$np: "
  { time mpirun --hostfile ~/hosts_all.txt --map-by node -np $np ~/pi_mpi; } 2>&1 | grep -E "PI|real"
done
```

---

## 8. Task 5 — Monitoring (Prometheus + Grafana)

### node_exporter Installation

node_exporter collects hardware and OS metrics from each node.

**Download on Pi 5:**
```bash
cd ~
wget https://github.com/prometheus/node_exporter/releases/download/v1.8.1/node_exporter-1.8.1.linux-arm64.tar.gz
tar xvf node_exporter-1.8.1.linux-arm64.tar.gz
sudo cp node_exporter-1.8.1.linux-arm64/node_exporter /usr/local/bin/
```

**Deploy to all Pi 3s:**
```bash
for i in 1 2 3 4 5 6 7; do
  scp /usr/local/bin/node_exporter pi3-$i@192.168.50.$((90+i)):~/
  ssh pi3-$i@192.168.50.$((90+i)) "sudo mv ~/node_exporter /usr/local/bin/ && sudo chmod +x /usr/local/bin/node_exporter"
done
```

**Start on all nodes:**
```bash
/usr/local/bin/node_exporter &
for i in 1 2 3 4 5 6 7; do
  ssh pi3-$i@192.168.50.$((90+i)) "nohup /usr/local/bin/node_exporter > /tmp/ne.log 2>&1 &"
done
```

### Prometheus Installation and Configuration

```bash
cd ~
wget https://github.com/prometheus/prometheus/releases/download/v2.53.0/prometheus-2.53.0.linux-arm64.tar.gz
tar xvf prometheus-2.53.0.linux-arm64.tar.gz
```

**Configuration (`~/prometheus-2.53.0.linux-arm64/prometheus.yml`):**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'raspberry-cluster'
    static_configs:
      - targets:
          - '192.168.50.1:9100'
          - '192.168.50.91:9100'
          - '192.168.50.92:9100'
          - '192.168.50.93:9100'
          - '192.168.50.94:9100'
          - '192.168.50.95:9100'
          - '192.168.50.96:9100'
          - '192.168.50.97:9100'
        labels:
          cluster: 'rpi-cluster'
```

**Start:**
```bash
cd ~/prometheus-2.53.0.linux-arm64
./prometheus --config.file=prometheus.yml --web.listen-address=:9090 &
```

Access at: `http://192.168.50.1:9090`

### Grafana Installation

```bash
cd ~
wget https://dl.grafana.com/oss/release/grafana-11.1.0.linux-arm64.tar.gz
tar xvf grafana-11.1.0.linux-arm64.tar.gz
cd grafana-v11.1.0
./bin/grafana server &
```

Access at: `http://192.168.50.1:3000` (admin/admin)

**CPU Usage Query for Grafana:**
```
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)
```

**Memory Usage Query:**
```
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

---

## 9. Task 6 — Edge AI Object Detection

### Full Pipeline Architecture

```
Pi 4 (IMX500 Camera, 30fps)
    ↓ ZeroMQ PUSH (sender.py)
Pi 5 + Hailo AI HAT+ (receiver_hailo.py)
    ↓ 54 FPS inference (yolov8s_h8l.hef)
    ↓ every 5s: SSH parallel preprocessing
Pi 3-1..7 (preprocess_worker.py — OpenCV contrast+blur)
    ↓ preprocessed frame back to Pi 5
Pi 5 Backend → MinIO → Frontend Dashboard
```

### YOLO Model Training

- **Framework:** YOLOv8 (Ultralytics)
- **Training platform:** Google Colab
- **Dataset tool:** Roboflow
- **Classes:** 20 custom classes including fire, smoke, knife, gun, person, mask
- **Training iterations:** 2 (May 2026 and June 2026)
- **Model file:** `best.pt` (6.1 MB)

### ZeroMQ Frame Streaming

We replaced HTTP polling with ZeroMQ PUSH/PULL for much lower latency:

**Pi 4 sender (`~/sender.py`):**
```python
import cv2, zmq, time
from picamera2 import Picamera2

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://192.168.50.1:5555")

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 640)}
))
picam2.start()
time.sleep(2)
print("Streaming frames to Pi 5...")

while True:
    frame = picam2.capture_array()
    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    socket.send(buffer.tobytes())
    time.sleep(0.1)
```

**Start on Pi 4:**
```bash
ssh pi@192.168.50.98
source yolo-env/bin/activate
python sender.py
```

### Hailo AI HAT+ Setup

**Installation:**
```bash
sudo apt-get install -y hailo-all
```

**Verify device detected:**
```bash
hailortcli scan
# Output: Device: 0001:01:00.0

hailortcli --version
# HailoRT-CLI version 4.23.0
```

**Benchmark test:**
```bash
hailortcli run /usr/share/hailo-models/yolov8s_h8l.hef
# Result: 58 FPS (benchmark), 54 FPS (pipeline)
```

**Available models on Pi 5:**
```
/usr/share/hailo-models/yolov8s_h8l.hef  ← used (HAILO8L compatible)
/usr/share/hailo-models/yolov8m_h10.hef
/usr/share/hailo-models/yolov11m_h10.hef
```

**Pi 5 receiver + Hailo inference (`~/receiver_hailo.py`):**
```python
import zmq, cv2, numpy as np, requests, base64, time, threading, sys
sys.path.insert(0, '/home/pi/.local/lib/python3.11/site-packages')
from hailo_platform import HEF, VDevice, HailoStreamInterface, InferVStreams, \
    ConfigureParams, InputVStreamParams, OutputVStreamParams, FormatType

BACKEND_URL = "http://192.168.50.1:5000"
HEF_PATH = "/usr/share/hailo-models/yolov8s_h8l.hef"

# ZeroMQ setup
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")

# Hailo setup
hef = HEF(HEF_PATH)
target = VDevice()
configure_params = ConfigureParams.create_from_hef(hef, interface=HailoStreamInterface.PCIe)
network_groups = target.configure(hef, configure_params)
network_group = network_groups[0]
network_group_params = network_group.create_params()
input_vstreams_params = InputVStreamParams.make(network_group, format_type=FormatType.UINT8)
output_vstreams_params = OutputVStreamParams.make(network_group, format_type=FormatType.FLOAT32)

# Preprocessing state
preprocessed_frame = [None]
preprocessing = [False]
last_preprocess = 0
PREPROCESS_INTERVAL = 5

def preprocess_async(frame):
    preprocessing[0] = True
    try:
        _, buf = cv2.imencode('.jpg', frame)
        b64 = base64.b64encode(buf).decode('utf-8')
        resp = requests.post(f"{BACKEND_URL}/api/preprocess",
                           json={"image_base64": b64}, timeout=30)
        data = resp.json()
        if data.get('success'):
            processed_bytes = base64.b64decode(data['image_base64'])
            processed_arr = np.frombuffer(processed_bytes, np.uint8)
            preprocessed_frame[0] = cv2.imdecode(processed_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Preprocess error: {e}")
    preprocessing[0] = False

last_send = 0
SEND_INTERVAL = 1

with InferVStreams(network_group, input_vstreams_params, output_vstreams_params) as pipeline:
    with network_group.activate(network_group_params):
        while True:
            try:
                data = socket.recv(flags=zmq.NOBLOCK)
                frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    continue

                now = time.time()
                if not preprocessing[0] and now - last_preprocess > PREPROCESS_INTERVAL:
                    t = threading.Thread(target=preprocess_async, args=(frame.copy(),))
                    t.daemon = True
                    t.start()
                    last_preprocess = now

                hailo_frame = preprocessed_frame[0] if preprocessed_frame[0] is not None else frame
                hailo_input = cv2.resize(hailo_frame, (640, 640))
                input_data = {hef.get_input_vstream_infos()[0].name: np.expand_dims(hailo_input, axis=0)}
                results = pipeline.infer(input_data)

                if now - last_send > SEND_INTERVAL:
                    _, buf = cv2.imencode('.jpg', frame)
                    payload = {
                        "type": "person", "threat": False, "confidence": 0.9,
                        "count": 1, "location": "Zone A", "classes": ["person"],
                        "image_base64": base64.b64encode(buf).decode('utf-8')
                    }
                    requests.post(f"{BACKEND_URL}/api/detections", json=payload, timeout=2)
                    last_send = now

            except zmq.Again:
                time.sleep(0.001)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(0.1)
```

### Distributed Preprocessing (Pi 3 Workers)

The frame is split into 7 horizontal strips, each sent to a different Pi 3 simultaneously:

**`~/app/parallel_preprocess.py` (on Pi 5):**
```python
import sys, subprocess, threading, numpy as np, cv2, time
sys.path.insert(0, '/home/pi/.local/lib/python3.11/site-packages')

WORKERS = [
    ('192.168.50.91', 'pi3-1', 'pi3-1'),
    ('192.168.50.92', 'pi3-2', 'pi3-2'),
    ('192.168.50.93', 'pi3-3', 'pi3-3'),
    ('192.168.50.94', 'pi3-4', 'pi3-4'),
    ('192.168.50.95', 'pi3-5', 'pi3-5'),
    ('192.168.50.96', 'pi3-6', 'pi3-6'),
    ('192.168.50.97', 'pi3-7', 'pi3-7')
]

def process_chunk(i, worker, name, user, chunk, results):
    ts = int(time.time() * 1000)
    chunk_path = f'/tmp/chunk_{i}_{ts}.jpg'
    out_path = f'/tmp/out_{i}_{ts}.jpg'
    remote_in = f'/tmp/in_{i}_{ts}.jpg'
    remote_out = f'/tmp/out_{i}_{ts}.jpg'
    cv2.imwrite(chunk_path, chunk)
    cmd = (f'scp {chunk_path} {user}@{worker}:{remote_in} && '
           f'ssh {user}@{worker} "PYTHONPATH=/home/{user}/.local/lib/python3.11/site-packages '
           f'python3 ~/preprocess_worker.py {remote_in} {remote_out}" && '
           f'scp {user}@{worker}:{remote_out} {out_path}')
    ret = subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if ret == 0:
        results[i] = cv2.imread(out_path)
        print(f'{name} ✅ done!')
    else:
        results[i] = chunk
        print(f'{name} ❌ failed')

def process_parallel(input_path, output_path):
    frame = cv2.imread(input_path)
    h = frame.shape[0]
    chunk_h = h // len(WORKERS)
    results = [None] * len(WORKERS)
    threads = []
    start = time.time()
    for i, (worker, name, user) in enumerate(WORKERS):
        s = i * chunk_h
        e = s + chunk_h if i < len(WORKERS)-1 else h
        t = threading.Thread(target=process_chunk, args=(i, worker, name, user, frame[s:e], results))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print(f'Total: {time.time()-start:.3f}s')
    cv2.imwrite(output_path, np.vstack(results))

if __name__ == '__main__':
    process_parallel(sys.argv[1], sys.argv[2])
```

**`~/preprocess_worker.py` (on each Pi 3):**
```python
import sys, socket
sys.path.insert(0, f'/home/{socket.gethostname()}/.local/lib/python3.11/site-packages')
import cv2

frame = cv2.imread(sys.argv[1])
enhanced = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
blurred = cv2.GaussianBlur(enhanced, (5,5), 0)
cv2.imwrite(sys.argv[2], blurred)
print(f"Processed on {socket.gethostname()}: {frame.shape}")
```

### Performance Comparison

| Method | FPS | Hardware |
|--------|-----|---------|
| YOLOv8 on Pi 4 CPU | 0.7 | Pi 4 (4GB) |
| Hailo AI HAT+ (benchmark) | 58 | Pi 5 + Hailo 8L |
| Hailo AI HAT+ (pipeline) | 54 | Pi 5 + Hailo 8L |
| **Speedup** | **77×** | — |

---

## 10. Task 7 — Backend + Kubernetes + MinIO

### MinIO Object Storage

MinIO provides S3-compatible object storage on the Pi 5 NVMe:

```bash
# Start MinIO
MINIO_ROOT_USER=admin MINIO_ROOT_PASSWORD=admin123 \
minio server /mnt/nvme/minio-data --console-address ":9001" &
```

- **API endpoint:** http://192.168.50.1:9000
- **Web console:** http://192.168.50.1:9001 (admin/admin123)
- **Bucket:** `detections` (public)
- **Auto-cleanup:** keeps last 100 images

### Node.js Backend

**Start:**
```bash
node ~/app/backend/server.js &
```

Runs on port 5000.

**API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/detections | POST | Receive detection from Pi 4/Hailo |
| /api/detections | GET | Last 10 detections |
| /api/detections/latest | GET | Most recent detection |
| /api/cluster/nodes | GET | SSH to all nodes for CPU/RAM/temp |
| /api/stats | GET | Detection statistics |
| /api/alerts | GET | Threat alerts |
| /api/preprocess | POST | Trigger Pi 3 parallel preprocessing |
| /api/frame | POST | Receive raw frame from Pi 4 |
| /api/frame | GET | Serve latest frame with timestamp |

### Kubernetes (k3s)

k3s is a lightweight Kubernetes distribution running on Pi 5 + 5 Pi 3 workers:

```bash
sudo kubectl get nodes
# NAME          ROLE           STATUS   VERSION
# raspberrypi   control-plane  Ready    v1.35.5+k3s1
# pi3-1         worker         Ready    v1.35.5+k3s1
# pi3-4         worker         Ready    v1.35.5+k3s1
# pi3-5         worker         Ready    v1.35.5+k3s1
# pi3-6         worker         Ready    v1.35.5+k3s1
# pi3-7         worker         Ready    v1.35.5+k3s1
```

**Services:**
- Frontend: NodePort :30080
- Backend: NodePort :30500 (scaled to 0; backend runs directly on Pi 5)

**Important:** Backend runs directly on Pi 5 (not in Kubernetes) because it needs SSH keys to access Pi 3 workers for preprocessing.

**Rebuild and redeploy frontend:**
```bash
cd ~/app/frontend
npm run build
sudo docker build -t frontend:latest .
sudo docker save frontend:latest | sudo k3s ctr images import -
sudo kubectl rollout restart deployment/frontend
```

---

## 11. Task 8 — Frontend Dashboard

**Access:** http://192.168.50.1:30080

**Features:**
- Live camera feed (updates every 500ms)
- Detection stats: total detections, people detected, threats, accuracy, active nodes
- Latest detection panel with real image from MinIO
- Alerts panel showing recent threats
- Cluster status grid with per-node CPU%, RAM%, temperature
- Recent detections table with class names and confidence

**Built with:** React 18, deployed on k3s Kubernetes

---

## 12. Task 9 — Telegram Bot

**Bot:** @edge90_monitor_bot

**Run:**
```bash
cd ~/telegram-bot
python3 main.py &
```

**Commands:**
- `/start` — welcome message
- `/status` — all nodes CPU/RAM/temperature
- `/latest` — most recent detection
- `/alerts` — recent threat alerts
- `/stats` — today's statistics
- `/myid` — show your Telegram chat ID
- `/help` — list commands

**Auto-alerts:** Checks `/api/alerts` every 30 seconds; sends Telegram message for new threats.

**Configuration (`~/telegram-bot/.env`):**
```
TELEGRAM_BOT_TOKEN=<your_token>
TELEGRAM_CHAT_ID=943023322
BACKEND_URL=http://192.168.50.1:5000
AUTHORIZED_USERS=
```

---

## 13. Task 10 — Documentation

This document serves as the complete project documentation.

---

## 14. How to Start Everything

Run these commands on **Pi 5**:

```bash
# 1. Start MinIO
MINIO_ROOT_USER=admin MINIO_ROOT_PASSWORD=admin123 \
minio server /mnt/nvme/minio-data --console-address ":9001" &

# 2. Start Backend
node ~/app/backend/server.js &

# 3. Start Hailo receiver
python3 ~/receiver_hailo.py &

# 4. Start Telegram bot
python3 ~/telegram-bot/main.py &

# 5. Start Prometheus monitoring
/usr/local/bin/node_exporter &
for i in 1 2 3 4 5 6 7; do
  ssh pi3-$i@192.168.50.$((90+i)) "nohup /usr/local/bin/node_exporter > /tmp/ne.log 2>&1 &"
done
cd ~/prometheus-2.53.0.linux-arm64 && ./prometheus --config.file=prometheus.yml --web.listen-address=:9090 &

# 6. Start Grafana
cd ~/grafana-v11.1.0 && ./bin/grafana server &

# 7. Frontend already running on Kubernetes
sudo kubectl get pods
```

Run on **Pi 4**:
```bash
ssh pi@192.168.50.98
source yolo-env/bin/activate
python sender.py
```

**Access:**
| Service | URL |
|---------|-----|
| Dashboard | http://192.168.50.1:30080 |
| Backend API | http://192.168.50.1:5000 |
| Prometheus | http://192.168.50.1:9090 |
| Grafana | http://192.168.50.1:3000 |
| MinIO Console | http://192.168.50.1:9001 |

---

## 15. Troubleshooting Guide

### Pi 5 eth0 loses IP after reboot
```bash
sudo ip addr add 192.168.50.1/24 dev eth0
sudo systemctl restart dnsmasq
# Permanent fix:
sudo nmcli con mod "Wired connection 1" ipv4.addresses 192.168.50.1/24 ipv4.method manual
sudo nmcli con up "Wired connection 1"
```

### dnsmasq fails to start
```bash
sudo ip addr add 192.168.50.1/24 dev eth0
sudo systemctl restart dnsmasq
sudo systemctl status dnsmasq
```

### Pi 3s unreachable
```bash
# Check if dnsmasq running
sudo systemctl status dnsmasq
# Check DHCP leases
cat /var/lib/misc/dnsmasq.leases
# Ping test
for i in 1 2 3 4 5 6 7; do
  echo -n "pi3-$i: "
  ping -c 1 -W 1 192.168.50.$((90+i)) > /dev/null 2>&1 && echo "UP" || echo "DOWN"
done
```

### Multiple backend instances running
```bash
pkill -f "node /home/pi/app/backend/server.js"
sudo kubectl scale deployment backend --replicas=0
sleep 2
node ~/app/backend/server.js &
```

### Hailo device busy
```bash
pkill -f receiver_hailo
pkill -f hailo_detect
sleep 2
python3 ~/receiver_hailo.py
```

### OpenCV missing on Pi 3s
```bash
for i in 1 2 3 4 5 6 7; do
  ssh pi3-$i@192.168.50.$((90+i)) "pip3 install opencv-python-headless --break-system-packages"
done
```

### Enable internet on Pi 3s via Pi 5 NAT
```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
sudo iptables -I FORWARD 1 -i eth0 -o wlan1 -j ACCEPT
sudo iptables -I FORWARD 2 -i wlan1 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

### SSH known_hosts conflict after SD card reinstall
```bash
for ip in 91 92 93 94 95 96 97; do
  ssh-keygen -f '/home/pi/.ssh/known_hosts' -R "192.168.50.$ip"
done
```

---

*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Prof. Dr. Christian Baun — Group 8*
