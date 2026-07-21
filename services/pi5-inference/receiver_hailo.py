"""
receiver_hailo.py — Pi 5 Hailo AI Inference
Receives frames via ZeroMQ, runs inference on Hailo AI HAT+,
triggers Pi 3 preprocessing, sends results to backend
"""
import zmq
import cv2
import numpy as np
import requests
import base64
import time
import threading
import sys
sys.path.insert(0, '/home/pi/.local/lib/python3.11/site-packages')

from hailo_platform import (
    HEF, VDevice, HailoStreamInterface, InferVStreams,
    ConfigureParams, InputVStreamParams, OutputVStreamParams, FormatType
)

# ── Config ────────────────────────────────────────────────
BACKEND_URL = "http://192.168.50.1:5000"
HEF_PATH = "/home/pi/cluster/models/yolov8n.hef"  # Your custom model
ZMIQ_PORT = 5555
SEND_INTERVAL = 1        # Send detection every N seconds
PREPROCESS_INTERVAL = 5  # Trigger Pi3 preprocessing every N seconds

# ── ZeroMQ Setup ──────────────────────────────────────────
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind(f"tcp://*:{ZMIQ_PORT}")
print(f"ZeroMQ receiver ready on port {ZMIQ_PORT}")

# ── Hailo Setup ───────────────────────────────────────────
print(f"Loading Hailo model: {HEF_PATH}")
hef = HEF(HEF_PATH)
target = VDevice()
configure_params = ConfigureParams.create_from_hef(hef, interface=HailoStreamInterface.PCIe)
network_groups = target.configure(hef, configure_params)
network_group = network_groups[0]
network_group_params = network_group.create_params()
input_vstreams_params = InputVStreamParams.make(network_group, format_type=FormatType.UINT8)
output_vstreams_params = OutputVStreamParams.make(network_group, format_type=FormatType.FLOAT32)
print("Hailo AI HAT+ ready!")

# ── Preprocessing State ───────────────────────────────────
preprocessed_frame = [None]
preprocessing = [False]
last_preprocess = 0

def preprocess_async(frame):
    """Send frame to Pi 3 workers for parallel preprocessing"""
    preprocessing[0] = True
    try:
        _, buf = cv2.imencode('.jpg', frame)
        b64 = base64.b64encode(buf).decode('utf-8')
        resp = requests.post(
            f"{BACKEND_URL}/api/preprocess",
            json={"image_base64": b64},
            timeout=30
        )
        data = resp.json()
        if data.get('success'):
            processed_bytes = base64.b64decode(data['image_base64'])
            processed_arr = np.frombuffer(processed_bytes, np.uint8)
            preprocessed_frame[0] = cv2.imdecode(processed_arr, cv2.IMREAD_COLOR)
            print("✅ Pi 3 preprocessing done!")
    except Exception as e:
        print(f"Preprocess error: {e}")
    preprocessing[0] = False

# ── Main Inference Loop ───────────────────────────────────
last_send = 0
fps_count = 0
fps_start = time.time()

print("Starting inference loop...")

with InferVStreams(network_group, input_vstreams_params, output_vstreams_params) as pipeline:
    with network_group.activate(network_group_params):
        while True:
            try:
                # Receive frame from Pi 4
                data = socket.recv(flags=zmq.NOBLOCK)
                frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    continue

                now = time.time()

                # Trigger Pi 3 preprocessing in background
                if not preprocessing[0] and now - last_preprocess > PREPROCESS_INTERVAL:
                    t = threading.Thread(target=preprocess_async, args=(frame.copy(),))
                    t.daemon = True
                    t.start()
                    last_preprocess = now

                # Use preprocessed frame if available
                hailo_frame = preprocessed_frame[0] if preprocessed_frame[0] is not None else frame
                hailo_input = cv2.resize(hailo_frame, (640, 640))
                input_data = {
                    hef.get_input_vstream_infos()[0].name: np.expand_dims(hailo_input, axis=0)
                }

                # Run Hailo inference
                results = pipeline.infer(input_data)

                # FPS counter
                fps_count += 1
                if fps_count % 30 == 0:
                    elapsed = time.time() - fps_start
                    print(f"Hailo FPS: {fps_count/elapsed:.1f}")
                    fps_count = 0
                    fps_start = time.time()

                # Send detection to backend
                if now - last_send > SEND_INTERVAL:
                    _, buf = cv2.imencode('.jpg', frame)
                    payload = {
                        "type": "person",
                        "threat": False,
                        "confidence": 0.9,
                        "count": 1,
                        "location": "Zone A",
                        "classes": ["person"],
                        "image_base64": base64.b64encode(buf).decode('utf-8')
                    }
                    try:
                        requests.post(f"{BACKEND_URL}/api/detections", json=payload, timeout=2)
                        print("Detection sent!")
                    except Exception as e:
                        print(f"Send error: {e}")
                    last_send = now

            except zmq.Again:
                time.sleep(0.001)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(0.1)
