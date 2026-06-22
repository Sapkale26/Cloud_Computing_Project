# Task 7 Report – Backend and Distributed Storage

## Task 7 Part A – Backend and Distributed Storage

### Approach

We developed a Node.js and Express-based backend API that acts as the communication layer between the Raspberry Pi object detection system, the frontend dashboard, and the Telegram bot. The backend provides REST API endpoints for detections, alerts, statistics, cluster node information, device information, and preprocessing requests.

The backend is designed to receive detection information from the Raspberry Pi camera and YOLO detection system. It can return the latest detections, provide recent alerts, expose system statistics, and support Telegram bot commands such as `/status`, `/latest`, `/alerts`, and `/stats`.

For storage, the project blueprint includes MinIO as S3-compatible object storage for detection images. Detection metadata is handled through backend API endpoints and database integration.

### Current Status

The backend API is implemented and tested locally. The Express server runs successfully, and the API endpoints return JSON responses as expected. PostgreSQL database integration has been configured and tested with event insertion and retrieval. Telegram-compatible endpoints have also been added and tested successfully with the Telegram bot.

Implemented and tested endpoints include:

- `GET /`
- `POST /events`
- `GET /events`
- `GET /api/cluster/nodes`
- `GET /api/detections`
- `GET /api/detections/latest`
- `GET /api/detection/latest`
- `POST /api/detections`
- `GET /api/alerts`
- `GET /api/stats`
- `GET /api/devices`
- `POST /api/preprocess`

The backend blueprint has been added to the repository under `backend/docs/backend-blueprint.md`.

### Lead

Purvesh Shapariya, with integration support from Janak.

---

## Task 7 Part B – Kubernetes Cluster and Distributed Preprocessing

### Approach

The second part of Task 7 focuses on deploying backend and frontend services in a Kubernetes environment and supporting distributed preprocessing across Raspberry Pi worker nodes. The planned setup uses k3s on the Raspberry Pi cluster, where the Raspberry Pi 5 acts as the control plane and Raspberry Pi 3 nodes act as workers.

The distributed preprocessing concept splits image frames into smaller parts and sends them to Raspberry Pi worker nodes for preprocessing. After preprocessing, the processed image parts are returned and merged before being used by the detection pipeline.

### Current Status

According to the current team progress report, the k3s cluster is operational and the frontend is deployed through Kubernetes. The backend currently runs directly on the Raspberry Pi 5 because SSH access to worker nodes from inside the container is difficult without mounting keys and configuring container permissions.

Distributed preprocessing is operational in a partial form. The current solution works, but processing time is still high because SSH and file transfer overhead add significant delay. Further optimization is needed before this can be considered real-time.

### Lead

Janak, with backend API support from Purvesh Shapariya.