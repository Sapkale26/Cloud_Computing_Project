import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN= os.getenv("TELEGRAM_BOT_TOKEN","")
BACKEND_URL= os.getenv("BACKEND_URL", "http://localhost:8080")
AUTHORIZED_USERS_RAW=os.getenv("AUTHORIZED_USERS", "")

AUTHORIZED_USERS = [
    int(user_id.strip())# 3. Se mete en la lista
    for user_id in AUTHORIZED_USERS_RAW.split(",")# 1. Comprueba que el user.id esté en la lista de números (split(","))
    if user_id.strip()# 2. Comprueba que el numero no sea vacio por una ultima coma en la lista
]