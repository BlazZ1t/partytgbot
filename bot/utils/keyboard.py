from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.models.user import User
from typing import List

def build_user_list_keyboard(users: List[User], current_page: int, total_pages: int):
    keyboard = []

    for user in users:
        full_name = f"{user.name} {user.surname}"
        user_button = InlineKeyboardButton("👤", url=f"tg://user?id={user.id}")
        inviter_button = InlineKeyboardButton("📨", url=f"tg://user?id={user.invited_by}") if user.invited_by else InlineKeyboardButton("N/A", callback_data="noop")
        row = [InlineKeyboardButton(full_name, callback_data="noop"), user_button, inviter_button]
        keyboard.append(row)
    
    pagination = []
    if current_page > 1:
        pagination.append(InlineKeyboardButton("⬅️", callback_data=f"page:{current_page - 1}"))
    pagination.append(InlineKeyboardButton(f"Page {current_page}/{total_pages}", callback_data="noop"))
    if current_page < total_pages:
        pagination.append(InlineKeyboardButton("➡️", callback_data=f"page:{current_page + 1}"))
    keyboard.append(pagination)

    return InlineKeyboardMarkup(keyboard)