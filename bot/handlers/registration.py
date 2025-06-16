from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from bot.database.mongo import get_users_col
from bot.models.user import User
from datetime import datetime

ASK_NAME, ASK_SURNAME = range(2)

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if get_users_col().find_one({"_id": user_id}):
        await update.message.reply_text("Похоже ты уже зарегестрированы! Давай тусоваться!")
        return ConversationHandler.END
    await update.message.reply_text("Привееет! Кажется мы ещё не знакомы, давай знакомиться, как тебя зовут?")
    return ASK_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("А фамилия?")
    return ASK_SURNAME

async def get_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["name"]
    surname = update.message.text.strip()
    user = User(
        _id=update.effective_user.id,
        name=name,
        surname=surname,
        registered_at=datetime.utcnow(),
    )
    get_users_col().insert_one(user.model_dump(by_alias=True))
    await update.message.reply_text(f"Добро пожаловать, {name} {surname}! Ты зарегистрирован.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Регистрация отменена. Напиши /start чтобы начать снова!")
    return ConversationHandler.END

def register(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", start_registration)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
