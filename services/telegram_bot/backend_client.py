import requests

from config import BACKEND_URL
        
def _get(endpoint: str, fallback):
    try: 
        response=requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return fallback
    
def get_cluster_nodes():
    return _get("/api/cluster/nodes",{"nodes":[]})
                
    
def get_latest_detection():
    return _get("/api/detections/latest",{})

def get_alerts():
    return _get("/api/alerts",{"alerts":[]}
)

def get_stats():
    return _get("/api/stats",
                {
                    "total_detections_today":0,
                    "total_people_detected":0,
                    "total_threats_detected":0,
                    "detection_accuracy":0,
                    "active_nodes":0,
                    "total_nodes": 0
                }
            )