from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from config import AUTHORIZED_USERS
from backend_client import get_cluster_nodes, get_alerts, get_latest_detection, get_stats


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
        await update.message.reply_text("⛔ You are not authorized to use this bot.")

    return True


def format_time(timestamp: str) -> str:
    if not timestamp:
        return "unknown"

    try:
        clean = timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        return dt.strftime("%H:%M:%S")
    except ValueError:
        return timestamp


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    await update.message.reply_text(
        "🖥️ *Edge Computing Monitor — Group 8*\n\n"
        "Available Commands:\n"
        "/status — Cluster node status\n"
        "/latest — Latest detection\n"
        "/alerts — Recent threat alerts\n"
        "/stats — Today's statistics\n"
        "/myid — Your Telegram ID\n"
        "/help — Show help",
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    await update.message.reply_text(
        "📖 *Available Commands*\n\n"
        "/start — Welcome message\n"
        "/status — All nodes CPU/RAM/temperature\n"
        "/latest — Latest detection with info\n"
        "/alerts — Recent threat alerts\n"
        "/stats — Today's detection statistics\n"
        "/myid — Show your Telegram ID\n"
        "/help — Show this help",
        parse_mode="Markdown"
    )


async def myId(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user is None:
        return

    await update.message.reply_text(
        f"Your Telegram ID: `{user.id}`",
        parse_mode="Markdown"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    data = get_cluster_nodes()
    nodes = data.get("nodes", [])

    lines = ["🖥️ *Cluster Status*\n"]
    active = 0

    for node in nodes:
        name = node.get("name", "unknown")
        role = node.get("role", "unknown")
        node_status = node.get("status", "unknown")
        cpu = node.get("cpu_percent", 0)
        memory = node.get("memory_percent", 0)
        temp = node.get("temperature", 0)

        if node_status.lower() in ["ready", "online"]:
            icon = "✅"
            active += 1
        else:
            icon = "❌"

        role_label = "Master" if role == "control-plane" else "Worker"

        lines.append(f"{icon} *{name}* ({role_label})")
        lines.append(f"   CPU: {cpu}% | RAM: {memory}% | 🌡️ {temp}°C")
        lines.append("")

    lines.append(f"Active: *{active}/{len(nodes)}* nodes")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown"
    )


async def latestDetection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    detection = get_latest_detection()

    if not detection.get("type"):
        await update.message.reply_text("No detections yet.")
        return

    detection_type = detection.get("type", "unknown")
    confidence = detection.get("confidence", 0)
    count = detection.get("count", 0)
    location = detection.get("location", "unknown")
    classes = detection.get("classes", [])
    timestamp = format_time(detection.get("timestamp", ""))
    threat = detection.get("threat", False)
    image_url = detection.get("image_url", "")

    text = (
        f"{'⚠️' if threat else '🎯'} *Latest Detection*\n\n"
        f"Type: {detection_type.capitalize()}\n"
        f"Threat: {'YES ⚠️' if threat else 'No ✅'}\n"
        f"Confidence: {round(confidence * 100, 1)}%\n"
        f"Count: {count}\n"
        f"Location: {location}\n"
        f"Classes: {', '.join(classes)}\n"
        f"Time: {timestamp}"
    )

    if image_url:
        await update.message.reply_photo(
            photo=image_url,
            caption=text,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="Markdown"
        )


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    data = get_alerts()
    alerts_list = data.get("alerts", [])

    if not alerts_list:
        await update.message.reply_text("🔔 No recent alerts. System is safe! ✅")
        return

    lines = ["🔔 *Recent Alerts*\n"]

    for alert in alerts_list:
        message = alert.get("message", "Unknown alert")
        timestamp = format_time(alert.get("timestamp", ""))
        ack = alert.get("acknowledged", False)

        lines.append(f"🔴 {message}")
        lines.append(f"   Time: {timestamp} | {'✓ Ack' if ack else 'Pending'}")
        lines.append("")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    data = get_stats()

    text = (
        f"📊 *Today's Statistics*\n\n"
        f"👁️ Total Detections: *{data.get('total_detections_today', 0)}*\n"
        f"👤 People Detected: *{data.get('total_people_detected', 0)}*\n"
        f"⚠️ Threats Detected: *{data.get('total_threats_detected', 0)}*\n"
        f"🎯 Accuracy: *{data.get('detection_accuracy', 0)}%*\n"
        f"🖥️ Active Nodes: *{data.get('active_nodes', 0)}/{data.get('total_nodes', 0)}*"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return

    await update.message.reply_text(
        "Unknown command. Use /help to see available commands."
    )