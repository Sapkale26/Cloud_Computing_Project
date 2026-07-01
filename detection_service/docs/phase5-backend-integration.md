# Phase 5 – Backend Integration

## Objective

The objective of this phase was to integrate the Python-based Detection Service with the Node.js backend and PostgreSQL database. The backend receives detection metadata from the detection service and stores it in the database.

---

## Components Integrated

- Node.js Backend API
- Python Detection Service
- PostgreSQL Database
- YOLOv8 Detection Model

---

## Integration Workflow

1. Backend server starts on port 3000.
2. Detection service runs YOLO object detection.
3. Detection metadata is generated.
4. Metadata is sent to backend using HTTP POST request.
5. Backend validates the request.
6. Detection information is stored in PostgreSQL.
7. Backend returns a successful JSON response.

---

## Testing

### Backend Server

```bash
cd backend
node server.js
```

Expected Output

```
Server started on port 3000
```

---

### Run Detection Service

```bash
cd detection_service
source venv/bin/activate
python -m app.detector
```

Expected Output

```
Loading YOLO model...
Running detection...
Metadata generated successfully.
Detected objects: 6
Status: 200
"success": true
```

---

### Verify Database

```sql
SELECT * FROM detections;
```

Expected Output

A new detection record should appear in the table.

---

### Backend Health Check

```bash
curl http://localhost:3000/api/health
```

Expected Output

```json
{
  "status": "healthy",
  "service": "edge-monitoring-backend"
}
```

---

## Result

Backend integration completed successfully.

The detection service communicates with the backend using REST API, and all detection metadata is successfully stored in PostgreSQL.

---

## Screenshots

- Backend Server Running
- Detection Service Output
- PostgreSQL Detection Table
- Backend Health API Response
