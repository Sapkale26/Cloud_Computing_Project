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
        
def _get(endpoint: str, fallback):
    try: 
        response=requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException:
        return fallback
    
def get_cluster_nodes():
    return _get("/api/cluster/nodes",{"nodes":[{"name":"raspberry",
                                                "role": "control-plane",
                                                "status": "ready",
                                                "cpu_percent": 45.5,
                                                "memory-percent": 62.1,
                                                "temperature":53.3,
                                                "uptime": "10 hours, 30 minutes"
                                                },
                                            {
                                                "name":"pi3-1",
                                                "role": "worker",
                                                "status": "ready",
                                                "cpu-percent": 12.5,
                                                "memory-percent":35.0,
                                                "temperature":48.1,
                                                "uptime": "10 hours, 30 minutes"
                                            }
                                        ]
                                    }
                )
    
def get_latest_detection():
    return _get("/api/detections/latest",
                    {
                        "id": 42,
                        "timestamp": "2026-06-16T14:30:00.000Z",
                        "type":"person",
                        "threat":False,
                        "confidence": 0.95,
                        "count": 3,
                        "location": "Zone A",
                        "classes": ["person", "smoke"],
                        "image_url":""
                    }
            )

def get_alerts():
    return _get("/api/alerts",{
        "alerts":[
            {
                "id":42,
                "timeestamp":"2026-06-16T14:29:58.000Z",
                "severity":"high",
                "message":"Threat at Zone B (knife)",
                "acknowledge":False,
                "image_url":""
            }
        ]
    }
)

def get_stats():
    return _get("/api/stats",
                {
                    "total_detections_today":142,
                    "total_people_detected":139,
                    "total_threats_detected":3,
                    "detection_accuracy":94.5,
                    "active_nodes":6,
                    "total_nodes": 7
                }
            )