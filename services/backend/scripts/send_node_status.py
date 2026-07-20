import requests

BACKEND_URL = "http://localhost:3000/api/cluster/nodes"

node_status = {
    "name": "raspberrypi",
    "role": "control-plane",
    "status": "Ready",
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "temperature": 52.3,
    "uptime": "10 hours, 30 minutes"
}

try:
    response = requests.post(BACKEND_URL, json=node_status)

    print("Status:", response.status_code)
    print("Response:", response.text)

except Exception as e:
    print("Error:", e)