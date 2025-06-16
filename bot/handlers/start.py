from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет!! Чтобы начать пользоваться ботом напиши /register")
def register(app: Application):
    app.add_handler(CommandHandler("start", start))