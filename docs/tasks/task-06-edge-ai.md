# Task 6 — Edge AI Object Detection

## Overview

We built a real-time threat detection system that:

1. Captures video at 30 FPS from a Sony IMX500 AI Camera on Pi 4
2. Streams frames via ZeroMQ to Pi 5
3. Runs inference at 59 FPS using Hailo AI HAT+ on Pi 5
4. Preprocesses frames in parallel across 7 Pi 3 workers
5. Detects 40 custom object classes including threats (fire, smoke, knife, gun)

**Performance:** 0.7 FPS (CPU) → 59 FPS (Hailo AI HAT+) — **84× speedup**

## Hardware

**Sony IMX500 AI Camera Module**

- Connected to Pi 4 via CSI ribbon cable
- On-sensor AI processing capability (used for capture only in our setup)
- Resolution: up to 12MP, used at 640×640 for inference

**Hailo AI HAT+ (Hailo-8L)**

- Connected to Pi 5 via PCIe M.2 slot
- 13 TOPS (Tera Operations Per Second)
- Runs compiled `.hef` model files
- Zero CPU usage during inference

## Custom YOLO Model

**Training**

- Framework: YOLOv8 (Ultralytics)
- Training platform: Google Colab (GPU)
- Dataset: Custom dataset built with Roboflow
- Iterations: 2 training runs (May 2026 and June 2026)
- Model file: `yolov8n.hef` (converted for Hailo-8L)

**Classes (40 total)**

- **Threat classes:** Gun, Knife, Weapon, Bomb, Bomb Recog, Grenade, fire, smoke
- **Other classes:** person, cat, dog, phone, cigarette, laptop, bottle, backpack, chair, door, house, light, pen, snake, sofa, vegetables, water, window, Mobile phone, Poly Bag, bird, Box

**Model Conversion**

The model was converted from YOLOv8 (`.pt`) to Hailo format (`.hef`) using the Hailo Dataflow Compiler, which quantizes the model to INT8 for efficient inference on the Hailo-8L chip.

## Pipeline Architecture

```
Pi 4 (IMX500 Camera)
  │ 30 FPS capture at 640×640
  │ JPEG encode at 80% quality
  ▼
ZeroMQ PUSH socket → port 5555
  │ ~100ms network latency
  ▼
Pi 5 ZeroMQ PULL socket
  │
  ├─► Hailo AI HAT+ inference (yolov8n.hef)
  │   59 FPS, Cortex-A55 NPU, HAILO8L, 13 TOPS
  │
  ├─► Every 5 seconds: parallel preprocessing
  │   SSH to all 7 Pi 3 workers
  │   Each worker processes 1/7 of frame
  │   OpenCV: contrast +20%, Gaussian blur 5×5
  │   Merge 7 strips back into full frame
  │
  ▼
Backend API (port 5000)
  │
  ├─► MinIO: save detection image
  ├─► WebSocket: push to frontend (port 5001)
  └─► /api/detections: REST endpoint
```

## Component 1: Pi 4 ZeroMQ Sender

### Why ZeroMQ instead of HTTP?

We initially used HTTP polling (`requests.post()` every 100ms) which caused:

- High CPU usage on Pi 4 (30% for HTTP overhead)
- Variable latency (10-200ms depending on connection)
- Backend overload from too many simultaneous connections

ZeroMQ PUSH/PULL is a message queue pattern designed for high-throughput streaming:

- Sub-millisecond latency
- Non-blocking sends
- Built-in buffering
- <5% CPU overhead

```python
# services/pi4-camera/sender.py
import cv2, zmq, time
from picamera2 import Picamera2

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://192.168.50.1:5555")

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 640)}))
picam2.start()
time.sleep(2)

FPS_LIMIT = 10  # 10 FPS to avoid backend overload
frame_interval = 1.0 / FPS_LIMIT

while True:
    start = time.time()
    frame = picam2.capture_array()
    _, buffer = cv2.imencode(".jpg", frame,
                              [cv2.IMWRITE_JPEG_QUALITY, 80])
    socket.send(buffer.tobytes())

    elapsed = time.time() - start
    if elapsed < frame_interval:
        time.sleep(frame_interval - elapsed)
```

**Start on Pi 4:**

```bash
ssh pi@192.168.50.98
source yolo-env/bin/activate
python sender.py
```

## Component 2: Pi 5 Hailo Inference Receiver

```python
# services/pi5-inference/receiver_hailo.py
import zmq, cv2, numpy as np, requests, base64, time, threading, sys
sys.path.insert(0, '/home/pi/.local/lib/python3.11/site-packages')
from hailo_platform import (
    HEF, VDevice, HailoStreamInterface, InferVStreams,
    ConfigureParams, InputVStreamParams, OutputVStreamParams, FormatType
)

BACKEND_URL = "http://192.168.50.1:5000"
HEF_PATH = "/home/pi/cluster/models/yolov8n.hef"

# ZeroMQ receiver
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")

def run_inference():
    # Initialize Hailo
    hef = HEF(HEF_PATH)
    target = VDevice()
    configure_params = ConfigureParams.create_from_hef(
        hef, interface=HailoStreamInterface.PCIe)
    network_groups = target.configure(hef, configure_params)
    network_group = network_groups[0]
    network_group_params = network_group.create_params()

    input_params = InputVStreamParams.make(
        network_group, format_type=FormatType.UINT8)
    output_params = OutputVStreamParams.make(
        network_group, format_type=FormatType.FLOAT32)

    with InferVStreams(network_group, input_params, output_params) as pipeline:
        with network_group.activate(network_group_params):
            while True:
                try:
                    data = socket.recv(flags=zmq.NOBLOCK)
                    frame = cv2.imdecode(
                        np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

                    # Run Hailo inference
                    hailo_input = cv2.resize(frame, (640, 640))
                    input_data = {
                        hef.get_input_vstream_infos()[0].name:
                            np.expand_dims(hailo_input, axis=0)
                    }
                    results = pipeline.infer(input_data)

                    # Send to backend every 1 second
                    # ... (see full code in services/pi5-inference/)

                except zmq.Again:
                    time.sleep(0.001)
                except Exception as e:
                    raise  # Triggers auto-restart

# Auto-restart wrapper
while True:
    try:
        run_inference()
    except Exception as e:
        print(f"Restarting in 3s: {e}")
        time.sleep(3)
```

**Start:**

```bash
python3 ~/cluster/services/pi5-inference/receiver_hailo.py &
```

## Component 3: Distributed Preprocessing (Pi 3 Workers)

Every 5 seconds, the latest frame is sent to all 7 Pi 3 workers simultaneously for parallel preprocessing.

### Why parallel preprocessing?

The preprocessed frames have improved contrast and reduced noise, potentially improving detection accuracy. The preprocessing runs in the background without affecting inference speed.

### How it works

```
Frame (640×640)
  │
  ├── Strip 1 (rows 0-91)   → Pi 3-1 (OpenCV: contrast+blur)
  ├── Strip 2 (rows 92-182) → Pi 3-2
  ├── Strip 3 (rows 183-273) → Pi 3-3
  ├── Strip 4 (rows 274-364) → Pi 3-4
  ├── Strip 5 (rows 365-455) → Pi 3-5
  ├── Strip 6 (rows 456-546) → Pi 3-6
  └── Strip 7 (rows 547-640) → Pi 3-7

  All 7 process simultaneously (in parallel)
  │
  └── Merge strips → Full preprocessed frame
```

### Pi 3 Worker Script

```python
# services/pi3-preprocessing/worker.py
# Deploy to: ~/preprocess_worker.py on each Pi 3
import sys, socket
sys.path.insert(0, f'/home/{socket.gethostname()}/.local/lib/python3.11/site-packages')
import cv2

frame = cv2.imread(sys.argv[1])

# Enhance contrast (+20% brightness, +20% contrast)
enhanced = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)

# Reduce noise with Gaussian blur
blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

cv2.imwrite(sys.argv[2], blurred)
print(f"Processed on {socket.gethostname()}: {frame.shape}")
```

### Parallel Preprocessing Manager

```python
# services/pi3-preprocessing/parallel_preprocess.py
def process_chunk(i, worker_ip, name, user, chunk, results):
    ts = int(time.time() * 1000)
    local_in = f'/tmp/chunk_{i}_{ts}.jpg'
    local_out = f'/tmp/out_{i}_{ts}.jpg'
    remote_in = f'/tmp/in_{i}_{ts}.jpg'
    remote_out = f'/tmp/out_{i}_{ts}.jpg'

    cv2.imwrite(local_in, chunk)
    cmd = (
        f'scp {local_in} {user}@{worker_ip}:{remote_in} && '
        f'ssh {user}@{worker_ip} '
        f'"python3 ~/preprocess_worker.py {remote_in} {remote_out}" && '
        f'scp {user}@{worker_ip}:{remote_out} {local_out}'
    )
    subprocess.call(cmd, shell=True)
    results[i] = cv2.imread(local_out)
```

Preprocessing time: ~3.5-5.6 seconds for 7 workers simultaneously.

## Performance Comparison

| Method | FPS | Hardware | Custom Classes |
|--------|-----|----------|------------------|
| YOLOv8 on Pi 4 CPU | 0.7 | Pi 4 Cortex-A72 | ✅ Yes (40 classes) |
| Hailo AI HAT+ (benchmark) | 59 | Pi 5 + Hailo 8L | ✅ Yes |
| Hailo AI HAT+ (pipeline) | 54-71 | Pi 5 + Hailo 8L | ✅ Yes |
| **Speedup** | **84×** | — | — |

### Why such a dramatic speedup?

| Aspect | CPU (Pi 4) | Hailo-8L |
|--------|-------------|----------|
| Architecture | General-purpose | Dedicated NPU |
| Operations | Sequential | Massively parallel |
| Power | 5-8W for inference | 2W for inference |
| Memory | LPDDR4 (bandwidth limited) | On-chip SRAM |
| Quantization | FP32 | INT8 (4× faster, same accuracy) |

## Verifying the Pipeline

```bash
# Check Hailo device
hailortcli scan
# Output: Hailo Devices: [-] Device: 0001:01:00.0

# Benchmark model performance
hailortcli run ~/cluster/models/yolov8n.hef
# Output: FPS: 59.16

# Check Pi 4 is sending frames
ssh pi@192.168.50.98 "ps aux | grep sender | grep -v grep"

# Check latest detection
curl -s http://192.168.50.1:5000/api/detections/latest | python3 -m json.tool \
  | grep -E "timestamp|classes|confidence|image_url"

# Check MinIO has new images
mc ls myminio/detections | tail -5
```

## Auto-Restart on Hailo Crash

The Hailo device occasionally crashes with DMA buffer errors after sustained inference. We implemented an auto-restart wrapper:

```python
# Main loop with auto-restart
while True:
    try:
        run_inference()  # Runs until crash
    except Exception as e:
        print(f"Restarting Hailo in 3 seconds... ({e})")
        time.sleep(3)
        # Loop continues, reinitializes Hailo
```

This ensures continuous operation without manual intervention.

---
*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Group 8*
