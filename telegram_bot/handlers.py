from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from config import AUTHORIZED_USERS
from backend_client import (
    get_devices,
    get_cluster_nodes,
    get_alerts,
    get_latest_detection,
    get_stats,
)


def is_authorized(user_id: int) -> bool:
    if not AUTHORIZED_USERS:
        return True
    return user_id in AUTHORIZED_USERS


async def reject_if_unauthorized(update: Update) -> bool:
    user = update.effective_user

    if user is None:
        return True

    if is_authorized(user.id):
        return False

    if update.message:
        await update.message.reply_text("You are not authorized to use this bot.")

    return True


def format_time(timestamp: str) -> str:
    if not timestamp:
        return "unknown"

    try:
        clean_timestamp = timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_timestamp)
        return dt.strftime("%H:%M:%S")
    except ValueError:
        return timestamp


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    await update.message.reply_text(
        """
Edge Computing Monitor started.

Available Commands:
/status - Show cluster node status
/latest - Show latest YOLO detection
/alerts - Show recent threat alerts
/stats - Show today's detection statistics
/help - Show help
/myid - Show your Telegram ID
        """.strip()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    await update.message.reply_text(
        """
Available Commands:

/start - Start the bot
/status - Show all nodes with CPU, RAM and temperature
/latest - Show latest detection with image
/alerts - Show recent threat alerts
/stats - Show today's detection statistics
/myid - Show your Telegram ID
/help - Show help
        """.strip()
    )


async def myId(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user is None:
        return

    await update.message.reply_text(f"Your Telegram ID is: {user.id}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    data = get_cluster_nodes()
    nodes = data.get("nodes", [])

    lines = ["🖥️ Cluster Status", ""]
    active_nodes = 0

    for node in nodes:
        name = node.get("name", "unknown")
        role = node.get("role", "unknown")
        status_value = node.get("status", "unknown")

        cpu = node.get("cpu_percent") or node.get("cpu") or "unknown"
        memory = node.get("memory_percent") or node.get("memory") or "unknown"
        temperature = node.get("temperature", "unknown")

        if str(status_value).lower() in ["ready", "online"]:
            icon = "✅"
            active_nodes += 1
        else:
            icon = "❌"

        role_label = "Master" if role == "control-plane" else "Worker"

        lines.append(f"{icon} {name} ({role_label})")
        lines.append(f"   CPU: {cpu}% | RAM: {memory}% | Temp: {temperature}°C")
        lines.append("")

    lines.append(f"Active: {active_nodes}/{len(nodes)} nodes")

    await update.message.reply_text("\n".join(lines))


async def latestDetection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    detection = get_latest_detection()

    detection_type = detection.get("type", "unknown")
    confidence = float(detection.get("confidence", 0) or 0)
    count = detection.get("count", 0)
    location = detection.get("location", "unknown")
    classes = detection.get("classes", [])
    timestamp = format_time(detection.get("timestamp", detection.get("created_at", "")))
    image_url = detection.get("image_url", "")

    confidence_percent = round(confidence * 100, 2)

    text = f"""
🎯 Latest Detection
Type: {detection_type}
Confidence: {confidence_percent}%
Count: {count}
Location: {location}
Classes: {", ".join(classes)}
Time: {timestamp}
    """.strip()

    if image_url and str(image_url).startswith("http"):
        await update.message.reply_photo(photo=image_url, caption=text)
    else:
        await update.message.reply_text(text)


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    data = get_alerts()
    alerts_list = data.get("alerts", [])

    if not alerts_list:
        await update.message.reply_text("🔔 No recent alerts.")
        return

    lines = ["🔔 Recent Alerts", ""]

    for alert in alerts_list:
        message = alert.get("message", "Unknown alert")
        timestamp = format_time(alert.get("timestamp", alert.get("created_at", "")))
        acknowledged = alert.get("acknowledged", False)
        acknowledged_text = "✓ Acknowledged" if acknowledged else "NOT acknowledged"

        lines.append(f"🔴 {message}")
        lines.append(f"   Time: {timestamp} | {acknowledged_text}")
        lines.append("")

    await update.message.reply_text("\n".join(lines))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    data = get_stats()

    text = f"""
📊 Today's Statistics
👁️ Total Detections: {data.get("total_detections_today", 0)}
👤 People Detected: {data.get("total_people_detected", 0)}
⚠️ Threats Detected: {data.get("total_threats_detected", 0)}
🎯 Accuracy: {data.get("detection_accuracy", 0)}%
🖥️ Active Nodes: {data.get("active_nodes", 0)}/{data.get("total_nodes", 0)}
    """.strip()

    await update.message.reply_text(text)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    await update.message.reply_text(
        "Unknown command, please select a new command. Use /help to view available commands"
    )