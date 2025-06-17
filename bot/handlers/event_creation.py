from telegram import Update
from telegram.ext import (ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, Application)

from bot.database.mongo import get_users_col, get_events_col
from bot.models.event import Event
from bot.utils.permissions import is_admin
import uuid
from datetime import datetime
from bot.utils.time import is_valid_datetime_string

(
    GET_NAME, GET_DESCRIPTION, GET_DISTRICT, GET_DATETIME, GET_ADDRESS, GET_CAPACITY
) = range(6)

async def start_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user = get_users_col().find_one({"_id": user_id})
    if not user:
        await update.message.reply_text("Видимо ты не зарегестрирован! Сначала напиши /register!")
        return ConversationHandler.END
    
    active_events = get_events_col().count_documents({
        "host_id": user_id,
        "cancelled": False,
        "expired": False,
    })
    if active_events >= 5 and not is_admin(user_id):
        await update.message.reply_text("Ты держишь уже 5 тусовок. Больше нельзя😞")
        return ConversationHandler.END
    
    await update.message.reply_text("Как назовём шашл?")
    return GET_NAME

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Опиши свою невъебенную хуету (без конфиденцильной информации, чтоб ебланы не пришли в 2 ночи)")
    return GET_DESCRIPTION

async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    await update.message.reply_text("В каком районе будет проходить шашл (это чтобы люди понимали в какую залупу им ехать)")
    return GET_DISTRICT

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["district"] = update.message.text
    await update.message.reply_text("А теперь ёбни полный адрес. Чурки увидят только после того как решат прийти")
    return GET_ADDRESS

async def get_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text("Когда и во сколько будет твоя хуйня? Попозже добавим норм считывание времени, чтобы ебланы как ты не проёбывались. Пока что пиши по типу 17-06-2025-18:00")
    return GET_DATETIME

async def get_capacity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["time"] = datetime.strptime(update.message.text, "%d-%m-%Y-%H:%M")
    except ValueError as e:
        await update.message.reply_text("EBLAN! Формат проверь сука. 17-06-2025-18:00")
        return GET_DATETIME
    await update.message.reply_text("Сколько людей готов вместить в свою богодельню?")
    return GET_CAPACITY

async def finalyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["capacity"] = int(update.message.text)
    except ValueError as e:
        await update.message.reply_text("Ебать дурень, циферками пиши")
        return GET_CAPACITY
    await update.message.reply_text("Всё, заебись, зарегали, вот что получилось\n" \
    f"Название: {context.user_data['name']}\n" \
    f"Дата: {context.user_data['time']}\n" \
    f"Адрес: {context.user_data['address']}, {context.user_data['district']}\n" \
    f"Описание: {context.user_data['description']} \n" \
    "\nПроверку и изменение данных потом добавим")

    user_id = update.effective_user.id
    user_data = context.user_data
    now = datetime.utcnow()

    event = Event(
        _id=str(uuid.uuid4()),
        name=user_data["name"],
        description=user_data["description"],
        district=user_data["district"],
        event_datetime=user_data["time"],
        address=user_data["address"],
        created_at=now,
        expired=False,
        canceled=False,
        capacity=user_data["capacity"],
        host_id=user_id,
        guests=[],
        invite_links=[],
    )

    get_events_col().insert_one(event.model_dump(by_alias=True))
    get_users_col().update_one(
        {"_id": user_id},
        {"$push": {"hosted_events": event.id}}
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Всё равно никто не пришёл бы, сука')
    return ConversationHandler.END

def register(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create_event", start_creation)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)],
            GET_DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            GET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_datetime)],
            GET_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_capacity)],
            GET_CAPACITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalyze)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)

