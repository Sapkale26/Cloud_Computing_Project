# Telegram Bot Blueprint — Edge Computing Alert System
## Cloud Computing SS2026 | Frankfurt UAS

---

## Overview

The Telegram bot sends **real-time alerts** when threats are detected by the YOLO camera on Pi 4. Users can also query system status via commands.

---

## Tech Stack & Packages

| Package | Purpose | Install |
|---------|---------|---------|
| `python-telegram-bot` | Telegram Bot API | `pip install python-telegram-bot==20.7` |
| `requests` | Call backend REST API | `pip install requests` |

---

## Setup Steps

### Step 1 — Create a Bot
1. Open Telegram → search **@BotFather**
2. Send `/newbot`
3. Name it: `EdgeComputingMonitor`
4. Username: `edge_monitor_bot`
5. Save the **TOKEN** BotFather gives you

### Step 2 — Get Your Chat ID
1. Start a chat with your bot
2. Send any message to it
3. Open: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Find `"chat":{"id": XXXXXXX}` — that is your Chat ID

---

## Bot Commands to Implement

| Command | What it should do |
|---------|-------------------|
| `/start` | Welcome message + list of commands |
| `/status` | Show all nodes with CPU, RAM, temperature |
| `/latest` | Show latest detection with image |
| `/alerts` | Show recent threat alerts |
| `/stats` | Show today's detection statistics |
| `/help` | Show all available commands |

---

## Data the Bot Gets from Backend

### For /status — call GET /api/cluster/nodes
```json
{
  "nodes": [
    {
      "name": "raspberrypi",
      "role": "control-plane",
      "status": "Ready",
      "cpu_percent": 45.2,
      "memory_percent": 62.1,
      "temperature": 52.3,
      "uptime": "10 hours, 30 minutes"
    },
    {
      "name": "pi3-1",
      "role": "worker",
      "status": "Ready",
      "cpu_percent": 12.5,
      "memory_percent": 35.0,
      "temperature": 48.1,
      "uptime": "10 hours, 30 minutes"
    }
  ]
}
```

### For /latest — call GET /api/detections/latest
```json
{
  "id": 42,
  "timestamp": "2026-06-16T14:30:00.000Z",
  "type": "person",
  "threat": false,
  "confidence": 0.95,
  "count": 3,
  "location": "Zone A",
  "classes": ["person", "smoke"],
  "image_url": "http://192.168.50.1:9000/detections/detection_42.jpg"
}
```

### For /alerts — call GET /api/alerts
```json
{
  "alerts": [
    {
      "id": 41,
      "timestamp": "2026-06-16T14:29:58.000Z",
      "severity": "high",
      "message": "Threat at Zone B (knife)",
      "acknowledged": false
    }
  ]
}
```

### For /stats — call GET /api/stats
```json
{
  "total_detections_today": 142,
  "total_people_detected": 139,
  "total_threats_detected": 3,
  "detection_accuracy": 94.5,
  "active_nodes": 6,
  "total_nodes": 7
}
```

---

## What Messages the Bot Should Send

### Automatic Threat Alert (sent every 30 seconds if new threat found)
```
⚠️ THREAT DETECTED!

📍 Location: Zone B
🔍 Object: knife
📊 Confidence: 87%
🕐 Time: 14:29:58
🆔 Detection ID: #41

[Send the detection image here]
```

### /status response
```
🖥️ Cluster Status

✅ raspberrypi (Master)
   CPU: 45.2% | RAM: 62.1% | Temp: 52.3°C

✅ pi3-1 (Worker)
   CPU: 12.5% | RAM: 35.0% | Temp: 48.1°C

✅ pi3-4 (Worker)
   CPU: 8.3% | RAM: 28.5% | Temp: 45.6°C

Active: 6/7 nodes
```

### /latest response
```
🎯 Latest Detection

Type: Person
Confidence: 95%
Count: 3
Location: Zone A
Classes: person, smoke
Time: 14:30:00

[Send the detection image here]
```

### /stats response
```
📊 Today's Statistics

👁️ Total Detections: 142
👤 People Detected: 139
⚠️ Threats Detected: 3
🎯 Accuracy: 94.5%
🖥️ Active Nodes: 6/7
```

### /alerts response
```
🔔 Recent Alerts

🔴 Threat at Zone B (knife)
   Time: 14:29:58 | NOT acknowledged

🔴 Threat at Zone A (gun)  
   Time: 14:25:10 | ✓ Acknowledged
```

---

## Important Logic

### Threat Detection Loop
- Run a background task every **30 seconds**
- Call `GET /api/alerts`
- For each alert where `acknowledged = false` → send Telegram message
- Keep track of which alert IDs already sent (avoid duplicates)

### Sending Images
- Get `image_url` from detection data
- Download the image from the URL
- Send it as a photo to Telegram chat

### Backend URL
```
http://192.168.50.1:5000
```
Must be connected to cluster network (192.168.50.x)

---

## File Structure

```
telegram-bot/
├── bot.py          ← Main bot file
├── config.py       ← BOT_TOKEN, CHAT_ID, BACKEND_URL
└── requirements.txt
```

---

## Development Tips

1. Test commands one by one — start with `/start`
2. Use mock data first — don't need the cluster to start
3. Add the threat alert loop last
4. Keep `BOT_TOKEN` secret — never commit to GitHub
5. Run on Pi 5 for 24/7 operation:
   ```bash
   python3 bot.py
   ```

---

*Frankfurt University of Applied Sciences — Cloud Computing SS2026*
