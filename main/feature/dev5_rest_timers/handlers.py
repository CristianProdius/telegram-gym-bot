import asyncio, re
from datetime import time
from aiogram import Router, F
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message, CallbackQuery

from .services import schedules, user_states, day_map, day_names, reminder_loop
from .keyboards import create_main_keyboard, create_day_keyboard, create_schedule_keyboard

router = Router()

# ==== Custom filter for HH:MM ====
class TimeFormatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(re.match(r'^\d{2}:\d{2}$', message.text))

# ==== /make_a_plan ====
@router.message(Command("make_a_plan"))
async def make_a_plan(message: Message):
    user_states[message.chat.id] = {'state': 'idle'}
    await message.answer("📅 Training planner — choose action:", reply_markup=create_main_keyboard())

# ==== Main actions ====
@router.callback_query(F.data.startswith('action_'))
async def handle_action(callback: CallbackQuery):
    action = callback.data.split('_')[1]
    chat_id = callback.message.chat.id

    if action == 'list':
        if chat_id not in schedules or not schedules[chat_id]:
            await callback.message.edit_text("📭 No trainings added", reply_markup=create_main_keyboard())
            return
        sorted_schedules = sorted(schedules[chat_id], key=lambda x: x[0])
        lst = '\n'.join(f"{day_names[d]} {t.hour:02}:{t.minute:02}" for d, t, _ in sorted_schedules)
        await callback.message.edit_text(f"📋 Your trainings:\n{lst}", reply_markup=create_main_keyboard())

    elif action == 'add':
        user_states[chat_id] = {'state': 'select_day_add'}
        await callback.message.edit_text("📅 Choose day of the week:", reply_markup=create_day_keyboard('add'))

    elif action == 'replace':
        keyboard = create_schedule_keyboard(chat_id)
        if not keyboard:
            await callback.message.edit_text("⚠ No trainings to replace", reply_markup=create_main_keyboard())
            return
        user_states[chat_id] = {'state': 'select_num_replace'}
        await callback.message.edit_text("🔄 Choose training to replace:", reply_markup=keyboard)

    await callback.answer()

# ==== Replace number ====
@router.callback_query(F.data.startswith('replace_num_'))
async def handle_replace_num(callback: CallbackQuery):
    num = int(callback.data.split('_')[2])
    chat_id = callback.message.chat.id

    if chat_id not in schedules or num < 0 or num >= len(schedules[chat_id]):
        await callback.message.edit_text("⚠ Invalid training number", reply_markup=create_main_keyboard())
        user_states[chat_id] = {'state': 'idle'}
        return

    user_states[chat_id] = {'state': 'select_day_replace', 'selected_num': num}
    await callback.message.edit_text("📅 Choose new day of the week:", reply_markup=create_day_keyboard('replace', num))
    await callback.answer()

# ==== Day selection ====
@router.callback_query(F.data.startswith(('add_day_', 'replace_day_')))
async def handle_day_selection(callback: CallbackQuery):
    parts = callback.data.split('_')
    action = parts[0]
    day_code = parts[2]
    chat_id = callback.message.chat.id

    if day_code not in day_map:
        await callback.message.edit_text("⚠ Invalid day", reply_markup=create_main_keyboard())
        user_states[chat_id] = {'state': 'idle'}
        return

    num = int(parts[3]) if action == 'replace' and len(parts) > 3 else None
    user_states[chat_id].update({
        'state': f'enter_time_{action}',
        'selected_day': day_code,
        'selected_num': num
    })
    await callback.message.edit_text("⌚ Enter time (HH:MM):")
    await callback.answer()

# ==== Time input ====
@router.message(TimeFormatFilter())
async def handle_time_input(message: Message, bot):
    chat_id = message.chat.id
    state_info = user_states.get(chat_id)

    if not state_info or state_info['state'] not in ['enter_time_add', 'enter_time_replace']:
        await message.answer("⚠ Use buttons to start", reply_markup=create_main_keyboard())
        return

    h, m = map(int, message.text.split(':'))
    train_time = time(h, m)
    weekday = day_map[state_info['selected_day']]

    if state_info['state'] == 'enter_time_add':
        if chat_id not in schedules:
            schedules[chat_id] = []
        if len(schedules[chat_id]) >= 5:
            lst = '\n'.join(f"{day_names[d]} {t.hour:02}:{t.minute:02}" for d, t, _ in schedules[chat_id])
            await message.answer(f"⚠ Already 5 trainings:\n{lst}\nUse Replace to modify.", reply_markup=create_main_keyboard())
            user_states[chat_id] = {'state': 'idle'}
            return
        task = asyncio.create_task(reminder_loop(bot, chat_id, weekday, train_time))
        schedules[chat_id].append((weekday, train_time, task))
        await message.answer("✅ Training added!", reply_markup=create_main_keyboard())

    else:  # enter_time_replace
        num = state_info['selected_num']
        if chat_id not in schedules or num < 0 or num >= len(schedules[chat_id]):
            await message.answer("⚠ Invalid training number", reply_markup=create_main_keyboard())
            user_states[chat_id] = {'state': 'idle'}
            return
        old_task = schedules[chat_id][num][2]
        old_task.cancel()
        try:
            await old_task
        except asyncio.CancelledError:
            pass
        task = asyncio.create_task(reminder_loop(bot, chat_id, weekday, train_time))
        schedules[chat_id][num] = (weekday, train_time, task)
        await message.answer("✅ Training replaced!", reply_markup=create_main_keyboard())

    user_states[chat_id] = {'state': 'idle'}
