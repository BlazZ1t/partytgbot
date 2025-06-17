from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Application
from bot.database.mongo import get_paginated_users, count_users
from bot.utils.keyboard import build_user_list_keyboard
from bot.utils.permissions import is_admin
from math import ceil

PAGE_SIZE = 5

async def admin_users_command(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Тебе нельзя использовать эту команду")
    total_users = count_users()
    total_pages = ceil(total_users / PAGE_SIZE)
    page = 1

    users = get_paginated_users(page, PAGE_SIZE)
    keyboard = build_user_list_keyboard(users, page, total_pages)
    await update.message.reply_text("Зарегестрированные пользователи:", reply_markup=keyboard)

async def user_pagination_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("❌ Тебе сюда нельзя", show_alert=True)
        return

    data = query.data

    if data.startswith("page:"):
        page = int(data.split(":")[1])
        total_users = count_users()
        total_pages = ceil(total_users / PAGE_SIZE)
        users = get_paginated_users(page, PAGE_SIZE)
        keyboard = build_user_list_keyboard(users, page, total_pages)
        await query.edit_message_reply_markup(reply_markup=keyboard)

def register(app: Application):
    app.add_handlers([
        CommandHandler("admin_users", admin_users_command),
        CallbackQueryHandler(user_pagination_callback, pattern=r"^page:\d+$")
    ])