
## Project Information
**Course:** Cloud Computing (SS2026)
**Task:** Task 7B - YOLO Detection Service Integration

# Detection Service

## Overview

The Detection Service is responsible for:

* Running YOLO object detection
* Processing images from sensor nodes
* Sending detection results to backend APIs
* Triggering Telegram notifications through the backend
* Providing event data to the frontend

---


## Phase 1 Completed

### Objective

Create the initial Detection Service structure.

### Completed Work

* Detection service directory created
* Project structure initialized
* Application folders created
* GitHub repository integration completed
* Feature branch created

### Directory Structure

detection_service/
├── app/
├── config/
├── docs/
├── images/
├── logs/
├── models/
├── tests/
├── Dockerfile
├── README.md
└── requirements.txt

---

## Phase 2 Completed

### Objective

Prepare Python environment and required dependencies.

### Completed Work

* Python virtual environment created
* pip upgraded
* Required packages installed:

  * ultralytics
  * opencv-python
  * requests
  * python-dotenv
  * numpy
  * pillow
* requirements.txt updated

### Verification

All required packages were successfully installed and verified.

---

## Current Status

Completed:

* Phase 1
* Phase 2

In Progress:

* Phase 3 (YOLO Detection Testing)

---

## Next Steps

* Download YOLO model
* Run object detection on sample images
* Generate detection metadata
* Integrate with backend APIs
* Store detection results
* Trigger Telegram notifications
