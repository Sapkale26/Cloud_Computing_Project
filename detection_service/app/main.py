import json
import logging
import sys
from pathlib import Path

from app.config import (
    INPUT_IMAGE,
    METADATA_DIR,
    METADATA_FILE,
    SEND_TO_BACKEND,
)
from app.detector import DetectionService


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("detection-service")


def save_metadata(metadata: dict) -> None:

    METADATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = METADATA_FILE.with_suffix(
        ".tmp"
    )

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )

    temporary_file.replace(
        METADATA_FILE
    )

    logger.info(
        "Metadata saved: %s",
        METADATA_FILE,
    )


def main() -> int:

    try:

        logger.info(
            "Starting Task 7B detection service"
        )

        logger.info(
            "Input image: %s",
            INPUT_IMAGE,
        )

        detector = DetectionService()

        metadata = detector.detect(
            INPUT_IMAGE
        )

        save_metadata(metadata)

        logger.info(
            "Detection completed successfully"
        )

        logger.info(
            "Objects detected: %d",
            metadata["count"],
        )

        logger.info(
            "Threat detected: %s",
            metadata["threat"],
        )

        for detection in metadata["detections"]:

            logger.info(
                "Detected %s | confidence=%.4f",
                detection["object_class"],
                detection["confidence"],
            )

        # Backend integration can be enabled later
        # after the API contract is confirmed.
        if SEND_TO_BACKEND:

            logger.warning(
                "SEND_TO_BACKEND is enabled, "
                "but backend integration should be "
                "configured through api_client.py."
            )

        return 0

    except FileNotFoundError as error:

        logger.error(
            "Required file not found: %s",
            error,
        )

        return 1

    except Exception as error:

        logger.exception(
            "Detection service failed: %s",
            error,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())
