"""
auto_scaler.py — Pi 3 Worker Auto-Scaler
Monitors cluster CPU via Prometheus and dynamically
adds/removes Pi 3 preprocessing workers based on load.
Sends Telegram alerts on scale events.
"""
import requests
import time

PROMETHEUS_URL = "http://192.168.50.1:9090"
BACKEND_URL = "http://192.168.50.1:5000"
TELEGRAM_TOKEN = "8627599199:AAEaeMcstYB6uEMBYAXYXxsCn05nUtKDMGI"
TELEGRAM_CHAT = "943023322"

SCALE_OUT_THRESHOLD = 70   # CPU% to add a worker
SCALE_IN_THRESHOLD = 30    # CPU% to remove a worker
CHECK_INTERVAL = 30        # seconds between checks
COOLDOWN = 120             # seconds between scale events
MIN_WORKERS = 2
MAX_WORKERS = 7

ALL_WORKERS = [
    ('192.168.50.91', 'pi3-1', 'pi3-1'),
    ('192.168.50.92', 'pi3-2', 'pi3-2'),
    ('192.168.50.93', 'pi3-3', 'pi3-3'),
    ('192.168.50.94', 'pi3-4', 'pi3-4'),
    ('192.168.50.95', 'pi3-5', 'pi3-5'),
    ('192.168.50.96', 'pi3-6', 'pi3-6'),
    ('192.168.50.97', 'pi3-7', 'pi3-7'),
]

active_workers = list(ALL_WORKERS[:MIN_WORKERS])


def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT, "text": msg},
            timeout=5
        )
    except Exception as e:
        print(f"Telegram error: {e}")


def get_cluster_cpu():
    try:
        instances = "|".join([f"{w[0]}:9100" for w in active_workers])
        query = f'100 - (avg(rate(node_cpu_seconds_total{{mode="idle",instance=~"{instances}"}}[1m])) * 100)'
        resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query}, timeout=5)
        result = resp.json()['data']['result']
        return float(result[0]['value'][1]) if result else 0.0
    except Exception as e:
        print(f"Prometheus error: {e}")
        return 0.0


def update_backend():
    try:
        worker_list = [{"ip": w[0], "name": w[1], "user": w[2]} for w in active_workers]
        requests.post(f"{BACKEND_URL}/api/workers", json={"workers": worker_list}, timeout=3)
    except Exception as e:
        print(f"Backend update error: {e}")


def scale_out():
    global active_workers
    if len(active_workers) >= MAX_WORKERS:
        return False
    for worker in ALL_WORKERS:
        if worker not in active_workers:
            active_workers.append(worker)
            update_backend()
            msg = (
                f"⬆️ AUTO SCALE OUT\n\n"
                f"High CPU detected!\n"
                f"Added: {worker[1]} ({worker[0]})\n"
                f"Active workers: {len(active_workers)}/{MAX_WORKERS}\n"
                f"Workers: {', '.join([w[1] for w in active_workers])}"
            )
            send_telegram(msg)
            print(f"Scale OUT: Added {worker[1]}. Active: {len(active_workers)}")
            return True
    return False


def scale_in():
    global active_workers
    if len(active_workers) <= MIN_WORKERS:
        return False
    removed = active_workers.pop()
    update_backend()
    msg = (
        f"⬇️ AUTO SCALE IN\n\n"
        f"Low CPU detected!\n"
        f"Removed: {removed[1]} ({removed[0]})\n"
        f"Active workers: {len(active_workers)}/{MAX_WORKERS}\n"
        f"Workers: {', '.join([w[1] for w in active_workers])}"
    )
    send_telegram(msg)
    print(f"Scale IN: Removed {removed[1]}. Active: {len(active_workers)}")
    return True


# Initialize
update_backend()
send_telegram(
    f"🚀 Auto-scaler started!\n"
    f"Min workers: {MIN_WORKERS} | Max: {MAX_WORKERS}\n"
    f"Scale OUT at: >{SCALE_OUT_THRESHOLD}% CPU\n"
    f"Scale IN at: <{SCALE_IN_THRESHOLD}% CPU\n"
    f"Initial workers: {', '.join([w[1] for w in active_workers])}"
)

print(f"Auto-scaler started. Monitoring {len(ALL_WORKERS)} Pi 3 workers...")
cooldown_remaining = 0

while True:
    try:
        cpu = get_cluster_cpu()
        print(f"Cluster CPU: {cpu:.1f}% | Active workers: {len(active_workers)}/{MAX_WORKERS}")

        if cooldown_remaining > 0:
            print(f"Cooldown: {cooldown_remaining}s remaining")
            cooldown_remaining = max(0, cooldown_remaining - CHECK_INTERVAL)
        else:
            if cpu > SCALE_OUT_THRESHOLD:
                if scale_out():
                    cooldown_remaining = COOLDOWN
            elif cpu < SCALE_IN_THRESHOLD:
                if scale_in():
                    cooldown_remaining = COOLDOWN

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(CHECK_INTERVAL)
