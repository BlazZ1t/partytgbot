import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS