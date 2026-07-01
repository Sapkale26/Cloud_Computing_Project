from app.api_client import send_detection
from ultralytics import YOLO
from datetime import datetime
import json

print("Loading YOLO model...")

model = YOLO("yolov8n.pt")

print("Running detection...")

results = model.predict(
    source="images/input/bus.jpg",
    save=True,
    project="images/output",
    name="result",
    conf=0.25
)

metadata = []

for result in results:
    for box in result.boxes:

        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])

        metadata.append({
            "timestamp": datetime.now().isoformat(),
            "object_class": class_name,
            "confidence": round(confidence, 4),
            "sensor_node_id": "pi4-01",
            "image_path": "images/output/result/bus.jpg"
        })

with open("logs/metadata/detection.json", "w") as file:
    json.dump(metadata, file, indent=4)

print("Metadata generated successfully.")
print(f"Detected objects: {len(metadata)}")
with open("logs/metadata/detection.json", "r") as f:
    detections = json.load(f)

payload = {
    "type": "object_detection",
    "threat": False,
    "confidence": detections[0]["confidence"] if detections else 0,
    "count": len(detections),
    "location": "sensor-node-pi4",
    "classes": [d["object_class"] for d in detections],
    "image_url": detections[0]["image_path"] if detections else ""
}

send_detection(payload)
