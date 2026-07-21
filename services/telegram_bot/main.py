from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from backend_client import get_alerts
from config import TELEGRAM_BOT_TOKEN
from handlers import (
    alerts,
    help_command,
    latestDetection,
    myId,
    start,
    status,
    stats,
    unknown_command,
)
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
sent_alert_ids = set()

async def check_threats(context):
    """Background job: send Telegram alert for new threats every 30s"""
    if not TELEGRAM_CHAT_ID:
        return

    data = get_alerts()
    for alert in data.get("alerts", []):
        alert_id = alert.get("id")
        acknowledged = alert.get("acknowledged", False)

        if alert_id and not acknowledged and alert_id not in sent_alert_ids:
            message = alert.get("message", "Unknown threat")
            timestamp = alert.get("timestamp", "")
            image_url = alert.get("image_url", "")

            text = (
                f"⚠️ THREAT DETECTED!\n\n"
                f"📍 {message}\n"
                f"🕐 {timestamp}\n"
                f"🆔 Detection ID: #{alert_id}"
            )

            try:
                if image_url:
                    import requests as req
                    img_resp = req.get(image_url, timeout=5)
                    if img_resp.status_code == 200:
                        await context.bot.send_photo(
                            chat_id=TELEGRAM_CHAT_ID,
                            photo=img_resp.content,
                            caption=text
                        )
                    else:
                        await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
                else:
                    await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)

                sent_alert_ids.add(alert_id)
                print(f"Threat alert sent: {message}")
            except Exception as e:
                print(f"Failed to send alert: {e}")
                
def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN not configured. Check the .env file."
        )

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("latest", latestDetection))
    app.add_handler(CommandHandler("alerts", alerts))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("myid", myId))

    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    app.job_queue.run_repeating(check_threats, interval=30, first=10)

    print("╔══════════════════════════════════════╗")
    print("║  @edge90_monitor_bot started!        ║")
    print("║  Checking threats every 30 seconds   ║")
    print("╚══════════════════════════════════════╝")
    app.run_polling()

if __name__ == "__main__":
    main()