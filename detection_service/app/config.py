from pathlib import Path
import os


# ============================================================
# Project Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = Path(
    os.getenv("MODEL_PATH", BASE_DIR / "best.pt")
)

INPUT_IMAGE = Path(
    os.getenv(
        "INPUT_IMAGE",
        BASE_DIR / "images" / "output" / "result" / "bus.jpg"
    )
)

OUTPUT_DIR = Path(
    os.getenv(
        "OUTPUT_DIR",
        BASE_DIR / "images" / "output"
    )
)

LOG_DIR = Path(
    os.getenv(
        "LOG_DIR",
        BASE_DIR / "logs"
    )
)

METADATA_DIR = LOG_DIR / "metadata"

METADATA_FILE = METADATA_DIR / "detection.json"


# ============================================================
# YOLO Inference Configuration
# ============================================================

CONFIDENCE_THRESHOLD = float(
    os.getenv("CONFIDENCE_THRESHOLD", "0.25")
)

IOU_THRESHOLD = float(
    os.getenv("IOU_THRESHOLD", "0.45")
)

IMAGE_SIZE = int(
    os.getenv("IMAGE_SIZE", "640")
)

DEVICE = os.getenv(
    "DEVICE",
    "cpu"
)

MAX_DETECTIONS = int(
    os.getenv("MAX_DETECTIONS", "100")
)


# ============================================================
# Sensor / Edge Node Configuration
# ============================================================

SENSOR_NODE_ID = os.getenv(
    "SENSOR_NODE_ID",
    "pi4-01"
)


# ============================================================
# Threat Classification
# ============================================================

THREAT_CLASSES = {
    "fire",
    "Gun",
    "Knife",
    "Weapon",
    "Bomb",
    "Bomb Recog",
    "Grenade",
}


# ============================================================
# Backend Configuration
# ============================================================

BACKEND_API_URL = os.getenv(
    "BACKEND_API_URL",
    ""
)


# ============================================================
# Runtime Configuration
# ============================================================

SAVE_DETECTION_IMAGE = os.getenv(
    "SAVE_DETECTION_IMAGE",
    "true"
).lower() == "true"

SEND_TO_BACKEND = os.getenv(
    "SEND_TO_BACKEND",
    "false"
).lower() == "true"
