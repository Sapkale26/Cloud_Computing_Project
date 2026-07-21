import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(ENV_PATH)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http:192.168.50.1:5000")

AUTHORIZED_USERS_RAW = os.getenv("AUTHORIZED_USERS", "")
AUTHORIZED_USERS = [
    int(user_id.strip())
    for user_id in AUTHORIZED_USERS_RAW.split(",")
    if user_id.strip()
]