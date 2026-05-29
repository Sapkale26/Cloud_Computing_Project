import requests

from config import BACKEND_URL

def get_devices():
    try: 
        response= requests.get(f"{BACKEND_URL}/api/devices", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return[        #Esto es solamente una simulacion hasta que tengamos el backend hecho, una vez tengamos el backend
                       #hecho, devolvera el primer return que tenemos antes de levantar la excepcion
            {
                "deviceId": "raspberry_master",
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
            }
        ]