# Object Detection System for Edge Computing (Task 6)

**Python** | **YOLOv8 (Ultralytics)** | **Raspberry Pi 4** | **OpenCV**

## Overview

This project implements a **real-time object detection system** as part of an edge computing monitoring solution. The system is designed to detect people and threat-related objects using a Raspberry Pi-based infrastructure and a custom-trained YOLO model.

The workflow includes dataset preparation, model training, evaluation, deployment, and real-time inference on edge devices.

---

## System Architecture

```text
Camera Input (Raspberry Pi Camera / Picamera2)
        |
Frame Capture (OpenCV)
        |
Preprocessing (format conversion)
        |
YOLO Model Inference (best.pt)
        |
Object Detection Output
        |
Visualization (bounding boxes)
        |
Real-time display / event monitoring
```

---

## Hardware Setup

| Component | Details |
|-----------|---------|
| Board | Raspberry Pi 4 Model B |
| Camera | Raspberry Pi AI Camera Module |
| Network | TP-Link Network Switch (cluster setup) |
| OS | Raspberry Pi OS (64-bit) |

---

## Software Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Core programming language |
| Google Colab | Model training environment |
| Roboflow | Dataset management |
| Git & GitHub | Version control |
| SCP | Secure model transfer |

---

## Full Installed Dependencies

### System Packages (Raspberry Pi OS)

```bash
python3  python3-pip  git  build-essential  cmake  pkg-config
libatlas-base-dev  libopenblas-dev  libjpeg-dev  libtiff5-dev
libpng-dev  libavcodec-dev  libavformat-dev  libswscale-dev
libv4l-dev  libxvidcore-dev  libx264-dev  libgtk-3-dev
dnsmasq  nfs-kernel-server  rsync  tcpdump
```

### Camera Stack (Raspberry Pi)

```text
libcamera
libcamera-apps
libcamera-dev
Raspberry Pi camera firmware drivers
picamera2 (Python API for libcamera)
```

### Python Libraries

```bash
pip install ultralytics torch torchvision opencv-python-headless numpy scipy matplotlib pandas roboflow
```

---

## Dataset Preparation

Two dataset versions were used for model training:

### Dataset Version 1
- Initial dataset used for baseline model training
- Limited number of annotated images
- Basic object coverage

### Dataset Version 2
- Expanded dataset using Roboflow
- Improved annotation quality
- Merged multiple datasets
- Increased class diversity and balance

---

## Object Classes

The model detects the following **20 classes**:

| # | Class | # | Class |
|---|-------|---|-------|
| 1 | Backpack | 11 | Knife |
| 2 | Bird | 12 | Laptop |
| 3 | Bottle | 13 | Pen |
| 4 | Cat | 14 | Person |
| 5 | Chair | 15 | Phone |
| 6 | Cigarette | 16 | Snake |
| 7 | Dog | 17 | Sofa |
| 8 | Door | 18 | Vegetables |
| 9 | Fire | 19 | Water |
| 10 | House | 20 | Window |

---

## Model Training

### Training Environment
- **Platform:** Google Colab GPU runtime
- **Base Model:** YOLOv8 pretrained (`yolov8n.pt`)

### Training Parameters

| Parameter | Value |
|-----------|-------|
| Image Size | 640 |
| Epochs | 50 |
| Batch Size | 16 |

### Training Command

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="dataset/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16
)
```

### Output Model
- `best.pt` saved from training run
- Transferred to Raspberry Pi using SCP

---

## Model Versions and Performance

### Version 1 - Initial Model
> Training Date: 28 May 2026

| Metric | Value |
|--------|-------|
| mAP@50 | 18.6% |
| Precision | 91.4% |
| Recall | 13.0% |
| F1 Score | 22.7% |

---

### Version 2 - Improved Model
> Training Date: 08 June 2026

| Metric | Value |
|--------|-------|
| mAP@50 | 41.5% |
| Precision | 54.9% |
| Recall | 34.0% |
| F1 Score | 42.0% |

---

## Model Deployment

### Transfer Method
Model transferred using **SCP (Secure Copy Protocol)** from local/Colab to Raspberry Pi.

### Deployment Location
/home/pi/yolo-env/best.pt

---

## Real-Time Inference (Raspberry Pi)

### Camera Verification
Camera tested using Picamera2 and libcamera stack.

Output frame shape:
(480, 640, 4)

### Detection Loop

```python
results = model(frame, conf=0.10, verbose=False)
```

Frame preprocessing:

```python
frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
```

---

## Observations

### Successfully Detected Objects
- Person
- Pen
- Phone

### Weak Detection Performance
- Bottle
- Small or occluded objects

---

## Known Limitations

- Reduced accuracy for small objects
- Class imbalance in dataset
- Limited edge device compute power
- Sensitivity to lighting conditions

---

## Future Improvements

- Expand dataset with real-world images
- Improve weak class detection (phone, bottle, knife)
- Train YOLOv8s or YOLOv8m models
- Optimize inference pipeline for Raspberry Pi
- Improve robustness in low-light environments

---

## Summary

This project demonstrates a complete end-to-end pipeline for edge-based object detection including:

- Dataset preparation and merging
- Model training in Google Colab
- Performance evaluation across iterations
- Deployment on Raspberry Pi
- Real-time object detection using OpenCV and Picamera2
