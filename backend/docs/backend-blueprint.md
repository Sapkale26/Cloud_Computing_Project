# Backend Blueprint — Edge Computing Monitoring System
## Cloud Computing SS2026 | Frankfurt UAS

---

## Overview

The backend is a **Node.js REST API** that:
- Receives real-time detection data from Pi 4 (YOLO camera)
- Stores detection images in MinIO (object storage)
- Provides cluster status by SSHing into each Pi node
- Serves data to the React frontend dashboard

---

## Tech Stack & Packages

| Package | Purpose | Install |
|---------|---------|---------|
| `express` | REST API framework | `npm install express` |
| `cors` | Allow frontend to call API | `npm install cors` |
| `node-ssh` | SSH into Pi nodes to get stats | `npm install node-ssh` |
| `minio` | Store/retrieve detection images | `npm install minio` |

---

## API Endpoints

### 1. POST /api/detections
**Called by:** Pi 4 YOLO detection script  
**Purpose:** Receive a detection event with image

**Request Body:**
```json
{
  "type": "person",
  "threat": false,
  "confidence": 0.95,
  "count": 3,
  "location": "Zone A",
  "classes": ["person", "smoke"],
  "image_base64": "<base64 encoded image>"
}
```

**Response:**
```json
{
  "success": true,
  "id": 42
}
```

---

### 2. GET /api/detections
**Called by:** Frontend dashboard  
**Purpose:** Return last 10 detections

**Response:**
```json
{
  "detections": [
    {
      "id": 42,
      "timestamp": "2026-06-16T14:30:00.000Z",
      "type": "person",
      "threat": false,
      "confidence": 0.95,
      "count": 3,
      "location": "Zone A",
      "classes": ["person", "smoke"],
      "image_url": "http://192.168.50.1:9000/detections/detection_42.jpg"
    },
    {
      "id": 41,
      "timestamp": "2026-06-16T14:29:58.000Z",
      "type": "threat",
      "threat": true,
      "confidence": 0.87,
      "count": 1,
      "location": "Zone B",
      "classes": ["knife"],
      "image_url": "http://192.168.50.1:9000/detections/detection_41.jpg"
    }
  ]
}
```

---

### 3. GET /api/detections/latest
**Called by:** Frontend (every 3 seconds)  
**Purpose:** Return the most recent detection

**Response:**
```json
{
  "id": 42,
  "timestamp": "2026-06-16T14:30:00.000Z",
  "type": "person",
  "threat": false,
  "confidence": 0.95,
  "count": 3,
  "location": "Zone A",
  "classes": ["person", "smoke"],
  "image_url": "http://192.168.50.1:9000/detections/detection_42.jpg"
}
```

---

### 4. GET /api/cluster/nodes
**Called by:** Frontend (every 8 seconds)  
**Purpose:** SSH into each Pi and get live CPU, RAM, temperature

**Response:**
```json
{
  "nodes": [
    {
      "name": "raspberrypi",
      "role": "control-plane",
      "ip": "192.168.50.1",
      "status": "Ready",
      "cpu_percent": 45.2,
      "memory_percent": 62.1,
      "temperature": 52.3,
      "uptime": "10 hours, 30 minutes"
    },
    {
      "name": "pi3-1",
      "role": "worker",
      "ip": "192.168.50.91",
      "status": "Ready",
      "cpu_percent": 12.5,
      "memory_percent": 35.0,
      "temperature": 48.1,
      "uptime": "10 hours, 30 minutes"
    },
    {
      "name": "pi3-4",
      "role": "worker",
      "ip": "192.168.50.94",
      "status": "Ready",
      "cpu_percent": 8.3,
      "memory_percent": 28.5,
      "temperature": 45.6,
      "uptime": "10 hours, 30 minutes"
    },
    {
      "name": "pi3-5",
      "role": "worker",
      "ip": "192.168.50.95",
      "status": "Ready",
      "cpu_percent": 31.6,
      "memory_percent": 21.0,
      "temperature": 49.4,
      "uptime": "10 hours, 31 minutes"
    },
    {
      "name": "pi3-6",
      "role": "worker",
      "ip": "192.168.50.96",
      "status": "Ready",
      "cpu_percent": 11.1,
      "memory_percent": 21.5,
      "temperature": 52.1,
      "uptime": "10 hours, 30 minutes"
    },
    {
      "name": "pi3-7",
      "role": "worker",
      "ip": "192.168.50.97",
      "status": "Ready",
      "cpu_percent": 29.4,
      "memory_percent": 23.8,
      "temperature": 51.0,
      "uptime": "10 hours, 31 minutes"
    }
  ]
}
```

---

### 5. GET /api/stats
**Called by:** Frontend (every 5 seconds)  
**Purpose:** Return summary statistics

**Response:**
```json
{
  "total_detections_today": 142,
  "total_people_detected": 139,
  "total_threats_detected": 3,
  "detection_accuracy": 94.5,
  "active_nodes": 6,
  "total_nodes": 7
}
```

---

### 6. GET /api/alerts
**Called by:** Frontend + Telegram bot  
**Purpose:** Return recent threat alerts

**Response:**
```json
{
  "alerts": [
    {
      "id": 41,
      "timestamp": "2026-06-16T14:29:58.000Z",
      "severity": "high",
      "message": "Threat at Zone B (knife)",
      "acknowledged": false
    },
    {
      "id": 38,
      "timestamp": "2026-06-16T14:25:10.000Z",
      "severity": "high",
      "message": "Threat at Zone A (gun)",
      "acknowledged": true
    }
  ]
}
```

---

### 7. POST /api/preprocess
**Called by:** Pi 4 before running YOLO  
**Purpose:** Send frame to Pi 3 workers for preprocessing

**Request Body:**
```json
{
  "image_base64": "<base64 encoded image>"
}
```

**Response:**
```json
{
  "success": true,
  "image_base64": "<base64 encoded preprocessed image>"
}
```

---

## How to Get Cluster Stats

For the `/api/cluster/nodes` endpoint, SSH into each Pi and run these shell commands:

| Data | Shell Command |
|------|--------------|
| CPU % | `top -bn1 \| grep 'Cpu(s)' \| awk '{print $2}'` |
| RAM % | `free \| grep Mem \| awk '{print $3/$2 * 100.0}'` |
| Temperature | `cat /sys/class/thermal/thermal_zone0/temp` (divide by 1000) |
| Uptime | `uptime -p` |

SSH credentials for all nodes:
- Username: `pi`
- Password: `1234`

---

## MinIO Image Storage

MinIO is already running on Pi 5. When you receive an image in POST /api/detections:
1. Decode the base64 image
2. Upload to MinIO bucket called `detections`
3. Return the public URL: `http://192.168.50.1:9000/detections/detection_<id>.jpg`

MinIO credentials:
- Endpoint: `192.168.50.1:9000`
- Access Key: `admin`
- Secret Key: `admin123`
- Bucket: `detections` (already created, public)

---

## Cluster Network

| Device | Hostname | IP | Role |
|--------|----------|----|------|
| Pi 5 | raspberrypi | 192.168.50.1 | Master + Backend |
| Pi 4 | raspberrypi4 | 192.168.50.98 | Camera + YOLO |
| Pi 3 | pi3-1 | 192.168.50.91 | Worker |
| Pi 3 | pi3-4 | 192.168.50.94 | Worker |
| Pi 3 | pi3-5 | 192.168.50.95 | Worker |
| Pi 3 | pi3-6 | 192.168.50.96 | Worker |
| Pi 3 | pi3-7 | 192.168.50.97 | Worker |

---

## Development Tips

1. Start with mock data — don't need the cluster to begin
2. Test endpoints with Postman or curl
3. Add SSH functionality last — needs cluster access
4. Run locally on `http://localhost:5000`
5. Frontend expects CORS to be enabled

---

*Frankfurt University of Applied Sciences — Cloud Computing SS2026*
