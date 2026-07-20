from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

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
    if not TELEGRAM_CHAT_ID:
        return
    from backend_client import get_alerts
    data = get_alerts()
    for alert in data.get("alerts", []):
        alert_id = alert.get("id")
        if alert_id and not alert.get("acknowledged") and alert_id not in sent_alert_ids:
            text = f"⚠️ THREAT DETECTED!\n\n📍 {alert.get('message')}\n🕐 {alert.get('timestamp')}\n🆔 #{alert_id}"
            await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
            sent_alert_ids.add(alert_id)
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

    print("Telegram Bot started.")
    app.job_queue.run_repeating(check_threats, interval=30, first=10)
    app.run_polling()

if __name__ == "__main__":
    main()