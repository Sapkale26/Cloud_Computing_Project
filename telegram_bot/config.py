import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN= os.getenv("TELEGRAM_BOT_TOKEN","")
BACKEND_URL= os.getenv("BACKEND_URL", "http://localhost:8080")
AUTHORIZED_USERS_RAW=os.getenv("AUTHORIZED_USERS", "")

AUTHORIZED_USERS = [
    int(user_id.strip())# 3. It gets into the list (just the number)
    for user_id in AUTHORIZED_USERS_RAW.split(",")# 1. Check the user is in the authorized users list (split(","))
    if user_id.strip()# 2. Checks the number is not null due to the last comma at the end
]