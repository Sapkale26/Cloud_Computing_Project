"""
worker.py (preprocess_worker.py on Pi 3s)
Applies OpenCV image enhancement to a frame strip.
Copy this to ~/preprocess_worker.py on each Pi 3.
"""
import sys
import socket

# Add local pip packages to path (Pi 3 specific)
hostname = socket.gethostname()
sys.path.insert(0, f'/home/{hostname}/.local/lib/python3.11/site-packages')

import cv2

def enhance_frame(input_path, output_path):
    """Apply contrast enhancement and Gaussian blur"""
    frame = cv2.imread(input_path)
    if frame is None:
        print(f"Error: could not read {input_path}")
        sys.exit(1)

    # Enhance contrast
    enhanced = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)

    # Apply slight blur to reduce noise
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

    cv2.imwrite(output_path, blurred)
    print(f"Processed on {hostname}: {frame.shape}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 worker.py <input.jpg> <output.jpg>")
        sys.exit(1)
    enhance_frame(sys.argv[1], sys.argv[2])
