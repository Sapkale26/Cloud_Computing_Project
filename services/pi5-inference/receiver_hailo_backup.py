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

BACKEND_URL = "http://192.168.50.1:5000"
HEF_PATH = "/home/pi/cluster/models/yolov8n.hef"
ZMIQ_PORT = 5555
SEND_INTERVAL = 1
PREPROCESS_INTERVAL = 5

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind(f"tcp://*:{ZMIQ_PORT}")
print(f"ZeroMQ receiver ready on port {ZMIQ_PORT}")

preprocessed_frame = [None]
preprocessing = [False]
last_preprocess = 0

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
            print("Pi 3 preprocessing done!")
    except Exception as e:
        print(f"Preprocess error: {e}")
    preprocessing[0] = False

def run_inference():
    global last_preprocess
    last_send = 0
    fps_count = 0
    fps_start = time.time()

    print("Loading Hailo model...")
    hef = HEF(HEF_PATH)
    target = VDevice()
    configure_params = ConfigureParams.create_from_hef(hef, interface=HailoStreamInterface.PCIe)
    network_groups = target.configure(hef, configure_params)
    network_group = network_groups[0]
    network_group_params = network_group.create_params()
    input_vstreams_params = InputVStreamParams.make(network_group, format_type=FormatType.UINT8)
    output_vstreams_params = OutputVStreamParams.make(network_group, format_type=FormatType.FLOAT32)
    print("Hailo ready! Starting inference...")

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

                    fps_count += 1
                    if fps_count % 30 == 0:
                        elapsed = time.time() - fps_start
                        print(f"Hailo FPS: {fps_count/elapsed:.1f}")
                        fps_count = 0
                        fps_start = time.time()

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
                    print(f"Hailo error: {e}")
                    raise  # Re-raise to trigger restart

# Main loop with auto-restart
while True:
    try:
        run_inference()
    except Exception as e:
        print(f"Restarting Hailo in 3 seconds... ({e})")
        time.sleep(3)
EOF
