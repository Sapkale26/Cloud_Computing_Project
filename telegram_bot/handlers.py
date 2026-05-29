from telegram import Update
from telegram.ext import ContextTypes

from config import AUTHORIZED_USERS
from backend_client import get_devices

def is_authorized(user_id: int) ->bool: #:int y -> son anotaciones del tipo de parametro que se deberia de estar entregando y devolviendo
    if not AUTHORIZED_USERS:
        return True
    
    return user_id in AUTHORIZED_USERS

async def reject_if_unauthorized(update: Update) ->bool:
    user=update.effective_user
    
    if user is None:
        return True
    if is_authorized(user.id):
        return False
    if update.message:
        await update.message.reply_text("You are not authorized to use this bot.")
        
    return True
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return
    
    await update.message.reply_text(
            """
        Raspberry System started.

        Available Commands:
        /status - Check the states of the Raspberries
        /help - See help
        /myid - Check your Telegram ID
                """.strip()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return
    await update.message.reply_text(
                """
        Available Commands:

        /start - Start the bot
        /status - Check System Status
        /myid - View your Telegram ID
        /help - Show help
                """.strip()
    )
    
async def myId(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user=update.effective_user
    if user is None:
        return 
    await update.message.reply_text(f"Your Telegram ID is: {user.id}")
    
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized(update):
        return
    devices= get_devices() 
    lines=["System State:", ""]
    for device in devices:
        device_id=device.get("deviceId","unknown")
        status_value=device.get("status", "unknown")
        role=device.get("role", "unknown")
        
        lines.append(f"{device_id}: {status_value}({role})")
        
    await update.message.reply_text("\n".join(lines))
    
async def unknown_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    if await reject_if_unauthorized():
        return
    
    await update.message.reply_text(
        "Unknown command, please select a new command. Use /help to view available commands"
    )
    