import requests

BACKEND_URL = "http://localhost:3000/api/detections"

def send_detection(payload):
    try:
        response = requests.post(
            BACKEND_URL,
            json=payload,
            timeout=10
        )

        print("Status:", response.status_code)
        print(response.text)

    except Exception as e:
        print("API Error:", e)
