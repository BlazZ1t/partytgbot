from telegram.ext import ApplicationBuilder
from bot.handlers import registration, event_creation, link_generation, admin
from bot.database.mongo import init_db
from dotenv import load_dotenv
import os
from pathlib import Path


# ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

def main():
    init_db()

    if Path(".env.dev").exists():
        load_dotenv(".env.dev")
    else:
        load_dotenv() 

    app = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build()
    registration.register(app)
    event_creation.register(app)
    link_generation.register(app)
    admin.register(app)


    app.run_polling()

if __name__ == '__main__':
    main()

