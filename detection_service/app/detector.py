from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ultralytics import YOLO

from app.config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    IMAGE_SIZE,
    DEVICE,
    MAX_DETECTIONS,
    THREAT_CLASSES,
    SENSOR_NODE_ID,
)


class DetectionService:
    """
    YOLO-based object detection service.

    Responsibilities:
    - Load and validate the custom YOLO model.
    - Perform inference.
    - Extract structured detections.
    - Calculate threat status.
    - Return normalized metadata.
    """

    def __init__(self) -> None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {MODEL_PATH}"
            )

        if MODEL_PATH.stat().st_size == 0:
            raise ValueError(
                f"YOLO model is empty: {MODEL_PATH}"
            )

        print(f"Loading YOLO model: {MODEL_PATH}")

        self.model = YOLO(str(MODEL_PATH))

        print("YOLO model loaded successfully.")
        print(f"Available classes: {self.model.names}")

    def detect(
        self,
        image_path: Path,
    ) -> dict[str, Any]:

        if not image_path.exists():
            raise FileNotFoundError(
                f"Input image not found: {image_path}"
            )

        results = self.model.predict(
            source=str(image_path),
            conf=CONFIDENCE_THRESHOLD,
            iou=IOU_THRESHOLD,
            imgsz=IMAGE_SIZE,
            device=DEVICE,
            max_det=MAX_DETECTIONS,
            verbose=False,
        )

        detections = []

        for result in results:

            for box in result.boxes:

                class_id = int(box.cls[0])

                confidence = float(box.conf[0])

                class_name = self.model.names[class_id]

                xyxy = [
                    round(float(value), 2)
                    for value in box.xyxy[0]
                ]

                is_threat = class_name in THREAT_CLASSES

                detections.append(
                    {
                        "object_class": class_name,
                        "class_id": class_id,
                        "confidence": round(confidence, 4),
                        "bounding_box": xyxy,
                        "threat": is_threat,
                    }
                )

        threat_detected = any(
            detection["threat"]
            for detection in detections
        )

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        return {
            "timestamp": timestamp,
            "sensor_node_id": SENSOR_NODE_ID,
            "image_path": str(image_path),
            "model": MODEL_PATH.name,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "detections": detections,
            "count": len(detections),
            "threat": threat_detected,
        }
