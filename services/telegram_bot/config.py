import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

AUTHORIZED_USERS_RAW = os.getenv("AUTHORIZED_USERS", "")

AUTHORIZED_USERS = [
    int(user_id.strip())
    for user_id in AUTHORIZED_USERS_RAW.split(",")
    if user_id.strip()
]