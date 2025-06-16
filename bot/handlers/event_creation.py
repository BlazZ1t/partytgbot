from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from bot.database.mongo import events_col, users_col
from bot.models.event import Event
from bot.utils.permissions import is_admin
import uuid
import datetime

# Define states
(
    GET_NAME, GET_DESCRIPTION, GET_DISTRICT,
    GET_DATETIME, GET_ADDRESS, GET_CAPACITY,
    CONFIRM_EVENT
) = range(7)

async def start_event_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_draft"] = {}
    user_id = update.effective_user.id

    user = users_col.find_one({"_id": user_id})
    if not user:
        await update.message.reply_text("Ты не зарегистрирован! Напиши /register сначала.")
        return ConversationHandler.END

    # Check active event limit unless admin
    active_events = events_col.count_documents({
        "host_id": user_id,
        "canceled": False,
        "expired": False
    })
    if active_events >= 5 and not is_admin(user_id):
        await update.message.reply_text("Ты уже хостишь 5 мероприятий. Больше нельзя 😞")
        return ConversationHandler.END

    await update.message.reply_text("Как назовем мероприятие?")
    return GET_NAME

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_draft"]["name"] = update.message.text
    await update.message.reply_text("Дай описание мероприятию (Не пиши здесь конфиденциальной информации):")
    return GET_DESCRIPTION

async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_draft"]["description"] = update.message.text
    await update.message.reply_text("В каком районе будет проходить мероприятие?")
    return GET_DISTRICT

async def get_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_draft"]["district"] = update.message.text
    await update.message.reply_text("Введите дату и время (в любом удобном формате):")
    return GET_DATETIME

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_draft"]["datetime"] = update.message.text
    await update.message.reply_text("Введите адрес проведения:")
    return GET_ADDRESS

async def get_capacity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_draft"]["address"] = update.message.text
    await update.message.reply_text("Введите лимит участников (число):")
    return GET_CAPACITY

async def get_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_draft"]["capacity"] = update.message.text
    return await show_confirmation(update, context)

async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    draft = context.user_data["event_draft"]
    text = (
        f"🔎 Проверьте информацию:\n\n"
        f"📛 Название: {draft['name']}\n"
        f"📝 Описание: {draft['description']}\n"
        f"📍 Район: {draft['district']}\n"
        f"📅 Дата и время: {draft['datetime']}\n"
        f"🏠 Адрес: {draft['address']}\n"
        f"👥 Лимит участников: {draft['capacity']}\n\n"
        f"Вы можете отредактировать любой пункт:"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📛 Название", callback_data="edit_name"),
         InlineKeyboardButton("📝 Описание", callback_data="edit_description")],
        [InlineKeyboardButton("📍 Район", callback_data="edit_district"),
         InlineKeyboardButton("📅 Дата и время", callback_data="edit_datetime")],
        [InlineKeyboardButton("🏠 Адрес", callback_data="edit_address"),
         InlineKeyboardButton("👥 Лимит", callback_data="edit_capacity")],
        [InlineKeyboardButton("✅ Всё верно", callback_data="confirm_event_creation")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_event_creation")]
    ])

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard)

    return CONFIRM_EVENT

async def handle_edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    field = query.data.split("_", 1)[1]  # e.g., name, description, etc.

    prompts = {
        "name": "Введите новое название:",
        "description": "Введите новое описание:",
        "district": "Введите новый район:",
        "datetime": "Введите новую дату и время:",
        "address": "Введите новый адрес:",
        "capacity": "Введите новый лимит участников:"
    }

    context.user_data["editing_field"] = field
    await query.edit_message_text(prompts[field])

    return {
        "name": GET_NAME,
        "description": GET_DESCRIPTION,
        "district": GET_DISTRICT,
        "datetime": GET_DATETIME,
        "address": GET_ADDRESS,
        "capacity": GET_CAPACITY
    }[field]

async def save_edited_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    field = context.user_data.pop("editing_field")
    context.user_data["event_draft"][field] = update.message.text
    return await show_confirmation(update, context)

async def finalize_event_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    draft = context.user_data["event_draft"]

    user_id = update.effective_user.id
    now = datetime.utcnow()

    event = Event(
        _id=str(uuid.uuid4()),
        name=draft["event_name"],
        description=draft["description"],
        district=draft["district"],
        event_datetime=draft["event_datetime"],
        address=draft["address"],
        created_at=now,
        expired=False,
        canceled=False,
        capacity=draft["capacity"],
        host_id=user_id,
        guests=[],
        invite_links=[]
    )
    events_col.insert_one(event.model_dump())

    # Update user hosted_events
    users_col.update_one(
        {"_id": user_id},
        {"$push": {"hosted_events": event._id}}
    )
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("✅ Событие успешно создано!")

    context.user_data.pop("event_draft", None)
    return ConversationHandler.END

async def cancel_event_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("❌ Создание события отменено.")
    context.user_data.pop("event_draft", None)
    return ConversationHandler.END

def get_event_creation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("create_event", start_event_creation)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)],
            GET_DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_datetime)],
            GET_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            GET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_capacity)],
            GET_CAPACITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_confirmation)],
            CONFIRM_EVENT: [
                CallbackQueryHandler(handle_edit_callback, pattern="^edit_"),
                CallbackQueryHandler(finalize_event_creation, pattern="^confirm_event_creation$"),
                CallbackQueryHandler(cancel_event_creation, pattern="^cancel_event_creation$")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_event_creation)],
        allow_reentry=True
    )
