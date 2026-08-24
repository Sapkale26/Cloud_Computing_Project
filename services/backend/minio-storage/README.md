# MinIO Storage Service

Object storage module for detection snapshot images, built on MinIO, an S3-compatible object store. This service persists detection images and exposes them as public URLs for the frontend.

## Responsibilities

- Initialize and configure the MinIO client
- Ensure the `detections` bucket exists with a public-read policy
- Upload base64-encoded detection images and return their public URL
- Periodically clean up old images so storage stays bounded

## Requirements

- Node.js 16+
- A running MinIO server reachable from this backend

## Installation

```bash
npm install
```

## Configuration

Copy `.env.example` to `.env` and adjust values for your environment.

| Variable | Default | Description |
|---|---|---|
| `MINIO_ENDPOINT` | `192.168.50.1` | Host running the MinIO server |
| `MINIO_PORT` | `9000` | MinIO API port |
| `MINIO_USE_SSL` | `false` | Set `true` if MinIO is served over HTTPS |
| `MINIO_ACCESS_KEY` | `admin` | MinIO access key |
| `MINIO_SECRET_KEY` | `admin123` | MinIO secret key |
| `MINIO_BUCKET` | `detections` | Bucket used to store images |
| `MINIO_MAX_IMAGES` | `100` | Max images retained before cleanup deletes the oldest |
| `MINIO_CLEANUP_INTERVAL_MS` | `300000` | How often the cleanup job runs (ms) |

## Usage

```javascript
const { ensureBucket, saveImage, startCleanupJob } = require('./minioService');

await ensureBucket();
startCleanupJob();

const imageUrl = await saveImage(base64ImageData, detectionId);
```

## Testing

```bash
npm test
```