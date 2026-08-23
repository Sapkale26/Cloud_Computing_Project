# Task 7 — Backend, Distributed Storage & Kubernetes

## Part A — Backend and Distributed Storage

### Approach

We developed a Node.js and Express-based backend API that acts as the communication layer between the Raspberry Pi object detection system, the frontend dashboard, and the Telegram bot. The backend provides REST API endpoints for detections, alerts, statistics, cluster node information, device information, and preprocessing requests.

The backend is designed to receive detection information from the Raspberry Pi camera and YOLO detection system. It can return the latest detections, provide recent alerts, expose system statistics, and support Telegram bot commands such as `/status`, `/latest`, `/alerts`, and `/stats`.

For storage, the project blueprint includes MinIO as S3-compatible object storage for detection images. Detection metadata is handled through backend API endpoints and database integration.

### Final Implementation Status

Task 7 Part A is **complete**. The backend was connected to PostgreSQL and updated to return real database records where available, with fallback data used only when database data is unavailable.

**Implemented backend features:**

- PostgreSQL database integration
- Detection event storage
- Alert storage and retrieval
- Cluster node status retrieval
- Statistics endpoint using stored database values
- Health check endpoint
- Test scripts for posting detection and node status data

**Endpoints implemented and tested:**

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Root/health |
| `/events` | POST | Submit event |
| `/events` | GET | List events |
| `/api/cluster/nodes` | GET | Cluster node status |
| `/api/detections` | GET | Full detection log |
| `/api/detections` | POST | Submit a detection |
| `/api/detections/latest` | GET | Most recent detection |
| `/api/detection/latest` | GET | (legacy singular alias) |
| `/api/alerts` | GET | Active/recent alerts |
| `/api/stats` | GET | Aggregate statistics |
| `/api/devices` | GET | Device/camera info |
| `/api/preprocess` | POST | Preprocessing request |
| `/api/health` | GET | Health check |

The backend blueprint is documented in the repository under `backend/docs/backend-blueprint.md`.

### Telegram Bot Integration

Telegram bot integration was also completed. The bot retrieves backend data and displays it using the following commands:

- `/status`
- `/latest`
- `/alerts`
- `/stats`
- `/myid`

Testing confirmed that data inserted through backend scripts is stored in PostgreSQL and correctly displayed through the Telegram bot. The image display flow was also tested successfully using an external image URL. The real YOLO image pipeline was left for later, since the Raspberry Pi YOLO detection script was not available in the repository at the time.

**Lead:** Janak, with backend API support from Purvesh Shapariya.

---

## Part B — Kubernetes Cluster and Distributed Preprocessing

### Approach

The second part of Task 7 focuses on deploying backend and frontend services in a Kubernetes environment and supporting distributed preprocessing across Raspberry Pi worker nodes. The setup uses **k3s** on the Raspberry Pi cluster, where the Raspberry Pi 5 acts as the control plane and the Raspberry Pi 3 nodes act as workers.

The distributed preprocessing concept splits image frames into smaller parts and sends them to Raspberry Pi worker nodes for preprocessing. After preprocessing, the processed image parts are returned and merged before being used by the detection pipeline.

### Status

The k3s cluster is operational and the **frontend is deployed through Kubernetes**. The **backend currently runs directly on the Raspberry Pi 5** (outside k3s), because SSH access to worker nodes from inside a container is difficult without mounting keys and configuring container permissions — the same trade-off documented in the frontend's deployment notes.

Distributed preprocessing is operational in a partial form. The current solution works, but processing time is still high because SSH and file transfer overhead add significant delay. Further optimization is needed before this can be considered real-time.

**Lead:** Purvesh Shapariya

---
*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Group 8*
