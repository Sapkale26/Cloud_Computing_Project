import requests

BACKEND_URL = "http://localhost:3000/api/detections"

detection = {
    "type": "person",
    "threat": False,
    "confidence": 0.95,
    "count": 2,
    "location": "Zone A",
    "classes": ["person"],
    "image_url": "https://picsum.photos/600/400"
}

try:
    response = requests.post(BACKEND_URL, json=detection)

    print("Status:", response.status_code)
    print("Response:", response.json())

except Exception as e:
    print("Error:", e)