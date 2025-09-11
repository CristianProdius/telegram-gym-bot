import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, BaseFilter
from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta, time
import re

router = Router()

async def make_a_plan(token: str):
    # Custom filter for time format (HH:MM)
    class TimeFormatFilter(BaseFilter):
        async def __call__(self, message: types.Message) -> bool:
            return bool(re.match(r'^\d{2}:\d{2}$', message.text))

    bot = Bot(token)
    dp = Dispatcher()

    # Store schedules: chat_id -> list of (weekday_int, time_obj, task)
    schedules = {}
    # Store user state: chat_id -> {state, selected_num, selected_day}
    user_states = {}

    day_map = {'Mo': 0, 'Tu': 1, 'We': 2, 'Th': 3, 'Fr': 4, 'Sa': 5, 'Su': 6}
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_codes = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

    async def reminder_loop(chat_id, weekday, train_time):
        while True:
            now = datetime.now()
            days_ahead = weekday - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_train_dt = now + timedelta(days=days_ahead)
            next_train_dt = next_train_dt.replace(hour=train_time.hour, minute=train_time.minute, second=0, microsecond=0)
            if next_train_dt <= now:
                next_train_dt += timedelta(days=7)
            next_reminder_dt = next_train_dt - timedelta(hours=1)
            if next_reminder_dt <= now:
                next_train_dt += timedelta(days=7)
                next_reminder_dt = next_train_dt - timedelta(hours=1)
            wait_seconds = (next_reminder_dt - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            try:
                await bot.send_message(chat_id, "Training in one hour!")
            except:
                pass  # Ignore sending errors

    def create_main_keyboard():
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Add", callback_data="action_add"),
             InlineKeyboardButton(text="List", callback_data="action_list"),
             InlineKeyboardButton(text="Replace", callback_data="action_replace")]
        ])
        return keyboard

    def create_day_keyboard(action, num=None):
        buttons = [[InlineKeyboardButton(text=day, callback_data=f"{action}_day_{code}")] for day, code in zip(day_names, day_codes)]
        if action == 'replace' and num is not None:
            for button in buttons:
                button[0].callback_data += f"_{num}"
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def create_schedule_keyboard(chat_id):
        if chat_id not in schedules or not schedules[chat_id]:
            return None
        buttons = []
        for i, (weekday, train_time, _) in enumerate(schedules[chat_id]):
            text = f"{day_names[weekday]} {train_time.hour:02}:{train_time.minute:02}"
            buttons.append([InlineKeyboardButton(text=text, callback_data=f"replace_num_{i}")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @dp.message(CommandStart())
    async def start(message: types.Message):
        chat_id = message.chat.id
        user_states[chat_id] = {'state': 'idle'}
        await bot.send_message(chat_id, "Hello! Choose an action:", reply_markup=create_main_keyboard())

    @dp.callback_query(lambda c: c.data.startswith('action_'))
    async def handle_action(callback: types.CallbackQuery):
        action = callback.data.split('_')[1]
        chat_id = callback.message.chat.id
        if action == 'list':
            if chat_id not in schedules or not schedules[chat_id]:
                await callback.message.edit_text("No trainings added", reply_markup=create_main_keyboard())
                return
            sorted_schedules = sorted(schedules[chat_id], key=lambda x: x[0])
            lst = '\n'.join(f"{day_names[d]} {t.hour:02}:{t.minute:02}" for d, t, _ in sorted_schedules)
            await callback.message.edit_text(f"Your trainings:\n{lst}", reply_markup=create_main_keyboard())
        elif action == 'add':
            user_states[chat_id] = {'state': 'select_day_add'}
            await callback.message.edit_text("Choose day of the week:", reply_markup=create_day_keyboard('add'))
        elif action == 'replace':
            keyboard = create_schedule_keyboard(chat_id)
            if not keyboard:
                await callback.message.edit_text("No trainings to replace", reply_markup=create_main_keyboard())
                return
            user_states[chat_id] = {'state': 'select_num_replace'}
            await callback.message.edit_text("Choose training to replace:", reply_markup=keyboard)
        await callback.answer()

    @dp.callback_query(lambda c: c.data.startswith('replace_num_'))
    async def handle_replace_num(callback: types.CallbackQuery):
        num = int(callback.data.split('_')[2])
        chat_id = callback.message.chat.id
        if chat_id not in schedules or num < 0 or num >= len(schedules[chat_id]):
            await callback.message.edit_text("Invalid training number", reply_markup=create_main_keyboard())
            user_states[chat_id] = {'state': 'idle'}
            return
        user_states[chat_id] = {'state': 'select_day_replace', 'selected_num': num}
        await callback.message.edit_text("Choose day of the week:", reply_markup=create_day_keyboard('replace', num))
        await callback.answer()

    @dp.callback_query(lambda c: c.data.startswith('add_day_') or c.data.startswith('replace_day_'))
    async def handle_day_selection(callback: types.CallbackQuery):
        parts = callback.data.split('_')
        action = parts[0]
        day_code = parts[2]
        chat_id = callback.message.chat.id
        if day_code not in day_map:
            await callback.message.edit_text("Invalid day", reply_markup=create_main_keyboard())
            user_states[chat_id] = {'state': 'idle'}
            return
        num = int(parts[3]) if action == 'replace' and len(parts) > 3 else None
        user_states[chat_id].update({
            'state': f'enter_time_{action}',
            'selected_day': day_code,
            'selected_num': num
        })
        await callback.message.edit_text("Enter time (e.g., 18:30):")
        await callback.answer()

    @dp.message(TimeFormatFilter())
    async def handle_time_input(message: types.Message):
        chat_id = message.chat.id
        if chat_id not in user_states or user_states[chat_id]['state'] not in ['enter_time_add', 'enter_time_replace']:
            await bot.send_message(chat_id, "Please use buttons to start the process", reply_markup=create_main_keyboard())
            return
        time_str = message.text
        try:
            h, m = map(int, time_str.split(':'))
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
            train_time = time(h, m)
        except:
            await bot.send_message(chat_id, "Invalid time format (HH:MM, 00:00-23:59)", reply_markup=create_main_keyboard())
            user_states[chat_id] = {'state': 'idle'}
            return
        state = user_states[chat_id]['state']
        day_code = user_states[chat_id]['selected_day']
        weekday = day_map[day_code]
        
        if state == 'enter_time_add':
            if chat_id not in schedules:
                schedules[chat_id] = []
            if len(schedules[chat_id]) >= 5:
                lst = '\n'.join(f"{day_names[d]} {t.hour:02}:{t.minute:02}" for d, t, _ in schedules[chat_id])
                await bot.send_message(chat_id, f"Already 5 trainings:\n{lst}\nChoose Replace to modify", reply_markup=create_main_keyboard())
                user_states[chat_id] = {'state': 'idle'}
                return
            task = asyncio.create_task(reminder_loop(chat_id, weekday, train_time))
            schedules[chat_id].append((weekday, train_time, task))
            await bot.send_message(chat_id, "Training added!", reply_markup=create_main_keyboard())
        else:  # enter_time_replace
            num = user_states[chat_id]['selected_num']
            if chat_id not in schedules or num < 0 or num >= len(schedules[chat_id]):
                await bot.send_message(chat_id, "Invalid training number", reply_markup=create_main_keyboard())
                user_states[chat_id] = {'state': 'idle'}
                return
            old_task = schedules[chat_id][num][2]
            old_task.cancel()
            try:
                await old_task
            except asyncio.CancelledError:
                pass
            task = asyncio.create_task(reminder_loop(chat_id, weekday, train_time))
            schedules[chat_id][num] = (weekday, train_time, task)
            await bot.send_message(chat_id, "Training replaced!", reply_markup=create_main_keyboard())
        
        user_states[chat_id] = {'state': 'idle'}

    await dp.start_polling(bot)