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
    app.run_polling()

if __name__ == "__main__":
    main()