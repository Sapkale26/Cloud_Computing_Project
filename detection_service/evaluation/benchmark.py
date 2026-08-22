import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import json
from pathlib import Path

from app.detector import DetectionService


TEST_DIR = Path("test_images")
RESULT_DIR = Path("evaluation/results")
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    detector = DetectionService()

    images = list(TEST_DIR.glob("*.jpg")) + list(TEST_DIR.glob("*.png"))

    if not images:
        print("No test images found.")
        return

    latencies = []

    for image in images:
        start = time.perf_counter()

        detector.detect(image)

        end = time.perf_counter()

        latency_ms = (end - start) * 1000
        latencies.append(latency_ms)

        print(f"{image.name}: {latency_ms:.2f} ms")

    average_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    average_fps = 1000 / average_latency

    results = {
        "images_processed": len(images),
        "average_latency_ms": round(average_latency, 2),
        "min_latency_ms": round(min_latency, 2),
        "max_latency_ms": round(max_latency, 2),
        "average_fps": round(average_fps, 2)
    }

    output_file = RESULT_DIR / "benchmark.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print("\nBenchmark completed.")
    print(json.dumps(results, indent=4))
    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()
