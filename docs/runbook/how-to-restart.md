# How to Start Everything

Run these commands on **Pi 5**:

```bash
# 1. Start MinIO
MINIO_ROOT_USER=$MINIO_ROOT_USER MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD \
minio server /mnt/nvme/minio-data --console-address ":9001" &

# 2. Start Backend
node ~/app/backend/server.js &

# 3. Start Hailo receiver
python3 ~/receiver_hailo.py &

# 4. Start Telegram bot
python3 ~/telegram-bot/main.py &

# 5. Start Prometheus monitoring
/usr/local/bin/node_exporter &
for i in 1 2 3 4 5 6 7; do
  ssh pi3-$i@192.168.50.$((90+i)) "nohup /usr/local/bin/node_exporter > /tmp/ne.log 2>&1 &"
done
cd ~/prometheus-2.53.0.linux-arm64 && ./prometheus --config.file=prometheus.yml --web.listen-address=:9090 &

# 6. Start Grafana
cd ~/grafana-v11.1.0 && ./bin/grafana server &

# 7. Frontend already running on Kubernetes
sudo kubectl get pods
```

Run on **Pi 4**:
```bash
ssh pi@192.168.50.98
source yolo-env/bin/activate
python sender.py
```

**Access:**
| Service | URL |
|---------|-----|
| Dashboard | http://192.168.50.1:30080 |
| Backend API | http://192.168.50.1:5000 |
| Prometheus | http://192.168.50.1:9090 |
| Grafana | http://192.168.50.1:3000 |
| MinIO Console | http://192.168.50.1:9001 |

---
