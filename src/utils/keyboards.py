from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from src.services.timer_service import timer_manager
from src.locales.translations import i18n

def build_timer_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Build timer configuration keyboard"""
    s = timer_manager.get_settings(user_id)
    text = f"⏱ {s['hours']}h {s['minutes']}m {s['seconds']}s"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=i18n.get_button("add_hour", user_id), callback_data="add_hour"),
            InlineKeyboardButton(text=i18n.get_button("add_minute", user_id), callback_data="add_minute"),
            InlineKeyboardButton(text=i18n.get_button("add_second", user_id), callback_data="add_second"),
        ],
        [
            InlineKeyboardButton(text=i18n.get_button("sub_hour", user_id), callback_data="sub_hour"),
            InlineKeyboardButton(text=i18n.get_button("sub_minute", user_id), callback_data="sub_minute"),
            InlineKeyboardButton(text=i18n.get_button("sub_second", user_id), callback_data="sub_second"),
        ],
        [InlineKeyboardButton(text=i18n.get_button("start", user_id), callback_data="start_timer")],
        [InlineKeyboardButton(text=i18n.get_button("stop", user_id), callback_data="stop_timer")],
        [InlineKeyboardButton(text=text, callback_data="noop")],
    ])

def create_exercise_keyboard(exercises: List) -> InlineKeyboardMarkup:
    """Create keyboard for exercise selection"""
    keyboard = []
    current_category = None

    for exercise in exercises:
        # Add category header if changed
        if exercise.category != current_category:
            current_category = exercise.category
            keyboard.append([
                InlineKeyboardButton(
                    text=f"📁 {current_category}",
                    callback_data="noop"
                )
            ])

        # Add exercise button
        keyboard.append([
            InlineKeyboardButton(
                text=exercise.name,
                callback_data=f"exercise:{exercise.id}"
            )
        ])

    # Add search button
    keyboard.append([
        InlineKeyboardButton(text="🔍 Search", callback_data="search_exercise")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_number_keyboard(min_val: int, max_val: int) -> InlineKeyboardMarkup:
    """Create keyboard for number selection"""
    keyboard = []
    row = []

    for i in range(min_val, min(max_val + 1, min_val + 20)):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"num:{i}"))

        if len(row) == 5:  # 5 buttons per row
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_main_menu_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """Create main menu keyboard"""
    keyboard = [
        [
            KeyboardButton(text="💪 Log Workout"),
            KeyboardButton(text="📊 Statistics")
        ],
        [
            KeyboardButton(text="⏱ Rest Timer"),
            KeyboardButton(text="🎯 My Routines")
        ],
        [
            KeyboardButton(text="📈 Progress"),
            KeyboardButton(text="⚙️ Settings")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        persistent=True
    )