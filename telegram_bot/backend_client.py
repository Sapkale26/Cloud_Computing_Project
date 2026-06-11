import requests

from config import BACKEND_URL

def get_devices():
    try: 
        response= requests.get(f"{BACKEND_URL}/api/devices", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return [        #This is only a simulation of how the data would look like
            {
                "deviceId": "raspberry_master1",
                "status": "online",
                "role": "master"
            },
            {
                "deviceId": "raspberry_master2",
                "status": "online",
                "role": "master"
            },
            {
                "deviceId": "raspberry_1",
                "status": "pending",
                "role": "camera"
            },
            {
                "deviceId": "raspberry_2",
                "status": "pending",
                "role": "sensor"
            },
            {
                "deviceId": "raspberry_3",
                "status": "pending",
                "role": "worker"
            },
            {
                "deviceId": "raspberry_4",
                "status": "pending",
                "role": "worker"
            },
            {
                "deviceId": "raspberry_5",
                "status": "pending",
                "role": "worker"
            },
            {
                "deviceId": "raspberry_6",
                "status": "pending",
                "role": "worker"
            },
            {
                "deviceId": "raspberry_7",
                "status": "pending",
                "role": "worker"
            }
        ]