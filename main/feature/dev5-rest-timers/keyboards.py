from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .services import settings

def build_timer_keyboard(user_id: int) -> InlineKeyboardMarkup:
    s = settings.get(user_id, {"hours": 0, "minutes": 0, "seconds": 0})
    text = f"⏱ {s['hours']}h {s['minutes']}m {s['seconds']}s"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Hours", callback_data="add_hour"),
            InlineKeyboardButton(text="➕ Minutes", callback_data="add_minute"),
            InlineKeyboardButton(text="➕ Seconds", callback_data="add_second"),
        ],
        [
            InlineKeyboardButton(text="➖ Hours", callback_data="sub_hour"),
            InlineKeyboardButton(text="➖ Minutes", callback_data="sub_minute"),
            InlineKeyboardButton(text="➖ Seconds", callback_data="sub_second"),
        ],
        [InlineKeyboardButton(text="Start ✅", callback_data="start_timer")],
        [InlineKeyboardButton(text="Stop ⛔", callback_data="stop_timer")],
        [InlineKeyboardButton(text=text, callback_data="noop")],
    ])
