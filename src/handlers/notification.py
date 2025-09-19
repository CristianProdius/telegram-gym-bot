"""Notification handlers for training reminders with i18n support"""

import re
from datetime import time
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.database.connection import get_session
from src.services.user_service import UserService
from src.services.notification_service import notification_service
from src.locales.translations import i18n

router = Router()
user_service = UserService()

class NotificationStates(StatesGroup):
    waiting_for_time_add = State()
    waiting_for_time_replace = State()

# Day mappings - now using translation keys
DAY_TRANSLATION_KEYS = ['day_monday', 'day_tuesday', 'day_wednesday', 'day_thursday', 'day_friday', 'day_saturday', 'day_sunday']
DAY_CODES = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
DAY_MAP = {code: idx for idx, code in enumerate(DAY_CODES)}

def get_day_names(user_id: int) -> list:
    """Get translated day names for user"""
    return [i18n.get(key, user_id) for key in DAY_TRANSLATION_KEYS]

def create_main_keyboard(user_id: int):
    """Create main notification menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=i18n.get("btn_add_training", user_id), callback_data="notif_add"),
            InlineKeyboardButton(text=i18n.get("btn_view_list", user_id), callback_data="notif_list")
        ],
        [
            InlineKeyboardButton(text=i18n.get("btn_replace_training", user_id), callback_data="notif_replace"),
            InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="notif_back")
        ]
    ])

def create_day_keyboard(user_id: int, action: str, notification_id: int = None):
    """Create day selection keyboard"""
    day_names = get_day_names(user_id)
    buttons = []
    
    for day_name, day_code in zip(day_names, DAY_CODES):
        callback_data = f"notif_{action}_day_{day_code}"
        if notification_id is not None:
            callback_data += f"_{notification_id}"
        buttons.append([InlineKeyboardButton(text=day_name, callback_data=callback_data)])
    
    buttons.append([InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="notif_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_notifications_keyboard(user_id: int, notifications):
    """Create keyboard for selecting notifications to replace"""
    day_names = get_day_names(user_id)
    buttons = []
    
    for notification in notifications:
        day_name = day_names[notification.weekday]
        time_str = notification.training_time.strftime("%H:%M")
        text = f"{day_name} {time_str}"
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=f"notif_select_{notification.id}"
        )])
    
    buttons.append([InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="notif_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def format_notifications_list(user_id: int, notifications) -> str:
    """Format notifications list for display"""
    day_names = get_day_names(user_id)
    notif_list = []
    
    for notif in notifications:
        day_name = day_names[notif.weekday]
        time_str = notif.training_time.strftime("%H:%M")
        notif_list.append(f"• {day_name} {time_str}")
    
    return "\n".join(notif_list)

@router.message(Command("notification"))
async def cmd_notification(message: types.Message):
    """Handle /notification command"""
    user_id = message.from_user.id
    
    # Update user language from database
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
    
    await message.answer(
        i18n.get("notification_menu", user_id),
        reply_markup=create_main_keyboard(user_id)
    )

@router.callback_query(F.data == "notif_add")
async def handle_add_notification(callback: types.CallbackQuery):
    """Handle add notification button"""
    user_id = callback.from_user.id
    
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
        
        notification_count = await notification_service.get_notification_count(session, user.id)
        
        if notification_count >= 5:
            notifications = await notification_service.get_user_notifications(session, user.id)
            notif_list = format_notifications_list(user_id, notifications)
            
            await callback.message.edit_text(
                i18n.get("notification_max_limit", user_id, notifications=notif_list),
                reply_markup=create_main_keyboard(user_id)
            )
            return
    
    await callback.message.edit_text(
        i18n.get("notification_add", user_id),
        reply_markup=create_day_keyboard(user_id, "add")
    )
    await callback.answer()

@router.callback_query(F.data == "notif_list")
async def handle_list_notifications(callback: types.CallbackQuery):
    """Handle list notifications button"""
    user_id = callback.from_user.id
    
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
        
        notifications = await notification_service.get_user_notifications(session, user.id)
        
        if not notifications:
            await callback.message.edit_text(
                i18n.get("notification_list_empty", user_id),
                reply_markup=create_main_keyboard(user_id)
            )
            return
        
        notif_list = format_notifications_list(user_id, notifications)
        
        await callback.message.edit_text(
            i18n.get("notification_list", user_id, notifications=notif_list),
            reply_markup=create_main_keyboard(user_id)
        )
    await callback.answer()

@router.callback_query(F.data == "notif_replace")
async def handle_replace_notification(callback: types.CallbackQuery):
    """Handle replace notification button"""
    user_id = callback.from_user.id
    
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
        
        notifications = await notification_service.get_user_notifications(session, user.id)
        
        if not notifications:
            await callback.message.edit_text(
                i18n.get("notification_replace_empty", user_id),
                reply_markup=create_main_keyboard(user_id)
            )
            return
        
        await callback.message.edit_text(
            i18n.get("notification_replace", user_id),
            reply_markup=create_notifications_keyboard(user_id, notifications)
        )
    await callback.answer()

@router.callback_query(F.data.startswith("notif_add_day_"))
async def handle_add_day_selection(callback: types.CallbackQuery, state: FSMContext):
    """Handle day selection for adding notification"""
    user_id = callback.from_user.id
    day_code = callback.data.split("_")[-1]
    
    if day_code not in DAY_MAP:
        await callback.answer("Invalid day selected", show_alert=True)
        return
    
    # Get user language
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
    
    await state.update_data(action="add", day_code=day_code)
    await state.set_state(NotificationStates.waiting_for_time_add)
    
    day_names = get_day_names(user_id)
    day_name = day_names[DAY_MAP[day_code]]
    
    await callback.message.edit_text(
        i18n.get("notification_set_time", user_id, day=day_name),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="notif_add")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("notif_select_"))
async def handle_notification_selection(callback: types.CallbackQuery, state: FSMContext):
    """Handle notification selection for replacement"""
    user_id = callback.from_user.id
    notification_id = int(callback.data.split("_")[-1])
    
    # Get user language
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
    
    await state.update_data(action="replace", notification_id=notification_id)
    await callback.message.edit_text(
        i18n.get("notification_replace", user_id),
        reply_markup=create_day_keyboard(user_id, "replace", notification_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("notif_replace_day_"))
async def handle_replace_day_selection(callback: types.CallbackQuery, state: FSMContext):
    """Handle day selection for replacing notification"""
    user_id = callback.from_user.id
    parts = callback.data.split("_")
    day_code = parts[3]
    notification_id = int(parts[4])
    
    if day_code not in DAY_MAP:
        await callback.answer("Invalid day selected", show_alert=True)
        return
    
    # Get user language
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
    
    await state.update_data(action="replace", day_code=day_code, notification_id=notification_id)
    await state.set_state(NotificationStates.waiting_for_time_replace)
    
    day_names = get_day_names(user_id)
    day_name = day_names[DAY_MAP[day_code]]
    
    await callback.message.edit_text(
        i18n.get("notification_set_new_time", user_id, day=day_name),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="notif_replace")]
        ])
    )
    await callback.answer()

@router.message(NotificationStates.waiting_for_time_add)
async def handle_time_input_add(message: types.Message, state: FSMContext):
    """Handle time input for adding notification"""
    user_id = message.from_user.id
    
    # Get user language
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
    
    if not re.match(r'^\d{2}:\d{2}$', message.text):
        await message.answer(i18n.get("notification_invalid_time_format", user_id))
        return
    
    try:
        hour, minute = map(int, message.text.split(':'))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time range")
        training_time = time(hour, minute)
    except ValueError:
        await message.answer(i18n.get("notification_invalid_time_range", user_id))
        return
    
    data = await state.get_data()
    day_code = data.get("day_code")
    weekday = DAY_MAP[day_code]
    
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        await notification_service.add_notification(session, user.id, weekday, training_time)
    
    day_names = get_day_names(user_id)
    day_name = day_names[weekday]
    time_str = training_time.strftime("%H:%M")
    
    await message.answer(
        i18n.get("notification_added", user_id, day=day_name, time=time_str),
        reply_markup=create_main_keyboard(user_id)
    )
    await state.clear()

@router.message(NotificationStates.waiting_for_time_replace)
async def handle_time_input_replace(message: types.Message, state: FSMContext):
    """Handle time input for replacing notification"""
    user_id = message.from_user.id
    
    # Get user language
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
    
    if not re.match(r'^\d{2}:\d{2}$', message.text):
        await message.answer(i18n.get("notification_invalid_time_format", user_id))
        return
    
    try:
        hour, minute = map(int, message.text.split(':'))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time range")
        training_time = time(hour, minute)
    except ValueError:
        await message.answer(i18n.get("notification_invalid_time_range", user_id))
        return
    
    data = await state.get_data()
    day_code = data.get("day_code")
    notification_id = data.get("notification_id")
    weekday = DAY_MAP[day_code]
    
    async with get_session() as session:
        await notification_service.update_notification(
            session, notification_id, weekday, training_time
        )
    
    day_names = get_day_names(user_id)
    day_name = day_names[weekday]
    time_str = training_time.strftime("%H:%M")
    
    await message.answer(
        i18n.get("notification_updated", user_id, day=day_name, time=time_str),
        reply_markup=create_main_keyboard(user_id)
    )
    await state.clear()

@router.callback_query(F.data == "notif_back")
async def handle_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    """Handle back to main menu"""
    user_id = callback.from_user.id
    
    # Get user language
    async with get_session() as session:
        user = await user_service.get_or_create_user(session, user_id)
        i18n.set_user_language(user_id, user.language_code)
    
    await state.clear()
    await callback.message.edit_text(
        i18n.get("notification_menu", user_id),
        reply_markup=create_main_keyboard(user_id)
    )
    await callback.answer()

def register_notification_handlers(dp):
    """Register notification handlers"""
    dp.include_router(router)