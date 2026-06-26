from ultralytics import YOLO

print("Loading YOLO model...")

# Load YOLOv8 Nano model
model = YOLO("yolov8n.pt")

print("Running detection...")

results = model.predict(
    source="images/input/bus.jpg",
    save=True,
    project="images/output",
    name="result",
    conf=0.25
)

print("Detection completed.")
