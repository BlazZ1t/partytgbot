from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
import os
from dotenv import load_dotenv
import requests
from io import BytesIO
from pathlib import Path

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if Path(".env.dev").exists():
        load_dotenv(".env.dev")
    else:
        load_dotenv() 
    user_id = update.effective_user.id
    payload = str(user_id)
    link = f"https://t.me/{os.getenv('BOT_USERNAME')}?start={payload}"
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={link}"

    response = requests.get(qr_api_url)
    image_bytes = BytesIO(response.content)

    caption = f"Вот твоя [ссылка приглашение]({link})\n{escape_markdown('Или просто отсканируй QR-код 📷', version=2)}"

    image_bytes.name = "invite_qr.png"
    await update.message.reply_photo(
        photo=image_bytes,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def register(app: Application):
    handler = CommandHandler("generate_link", get_link)
    app.add_handler(handler)