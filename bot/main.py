from telegram.ext import ApplicationBuilder
from bot.handlers import registration, start
from bot.database.mongo import init_db
from dotenv import load_dotenv
import os

load_dotenv()

# ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

def main():
    init_db()

    app = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build()
    start.register(app)
    registration.register(app)

    app.run_polling()

if __name__ == '__main__':
    main()

