import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from .services import timers, settings, Timer
from .keyboards import build_timer_keyboard

router = Router()

async def refresh_config_message(callback: CallbackQuery, user_id: int):
    await callback.message.edit_text(
        "Hello! 👋 Set your timer:",
        reply_markup=build_timer_keyboard(user_id)
    )

# ==== Start ====
@router.message(Command("timer"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}
    await message.answer("Hello! 👋 Set your timer:", reply_markup=build_timer_keyboard(user_id))

# ==== Increment / Decrement Handlers ====
@router.callback_query(F.data == "add_hour")
async def add_hour(callback: CallbackQuery):
    user_id = callback.from_user.id
    settings[user_id]["hours"] += 1
    await refresh_config_message(callback, user_id)
    await callback.answer("➕ 1 hour")

@router.callback_query(F.data == "add_minute")
async def add_minute(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["minutes"] < 59:
        settings[user_id]["minutes"] += 1
    else:
        settings[user_id]["minutes"] = 0
        settings[user_id]["hours"] += 1
    await refresh_config_message(callback, user_id)
    await callback.answer("➕ 1 minute")

@router.callback_query(F.data == "add_second")
async def add_second(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["seconds"] < 59:
        settings[user_id]["seconds"] += 1
    else:
        settings[user_id]["seconds"] = 0
        if settings[user_id]["minutes"] < 59:
            settings[user_id]["minutes"] += 1
        else:
            settings[user_id]["minutes"] = 0
            settings[user_id]["hours"] += 1
    await refresh_config_message(callback, user_id)
    await callback.answer("➕ 1 second")

# ==== Decrement ====
@router.callback_query(F.data == "sub_hour")
async def sub_hour(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["hours"] > 0:
        settings[user_id]["hours"] -= 1
    await refresh_config_message(callback, user_id)
    await callback.answer("➖ 1 hour")

@router.callback_query(F.data == "sub_minute")
async def sub_minute(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["minutes"] > 0:
        settings[user_id]["minutes"] -= 1
    elif settings[user_id]["hours"] > 0:
        settings[user_id]["hours"] -= 1
        settings[user_id]["minutes"] = 59
    await refresh_config_message(callback, user_id)
    await callback.answer("➖ 1 minute")

@router.callback_query(F.data == "sub_second")
async def sub_second(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["seconds"] > 0:
        settings[user_id]["seconds"] -= 1
    elif settings[user_id]["minutes"] > 0:
        settings[user_id]["minutes"] -= 1
        settings[user_id]["seconds"] = 59
    elif settings[user_id]["hours"] > 0:
        settings[user_id]["hours"] -= 1
        settings[user_id]["minutes"] = 59
        settings[user_id]["seconds"] = 59
    await refresh_config_message(callback, user_id)
    await callback.answer("➖ 1 second")

# ==== Start Timer ====
@router.callback_query(F.data == "start_timer")
async def start_timer(callback: CallbackQuery):
    user_id = callback.from_user.id
    s = settings[user_id]
    total_seconds = s["hours"] * 3600 + s["minutes"] * 60 + s["seconds"]

    if total_seconds <= 0:
        await callback.answer("⚠️ Time not set", show_alert=True)
        return

    timer = Timer(total_seconds)
    timer.start()
    timers[user_id] = timer

    async def notify():
        try:
            await asyncio.sleep(total_seconds)
            if user_id in timers and timers[user_id] == timer:
                del timers[user_id]
                settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}
                await callback.message.answer(
                    "✅ Timer completed!\n\n🔄 Want to start a new one?",
                    reply_markup=build_timer_keyboard(user_id)
                )
        except asyncio.CancelledError:
            pass

    timer.task = asyncio.create_task(notify())
    await callback.message.answer(f"⏳ Timer for {total_seconds} seconds started!")
    await callback.answer()

# ==== Stop Timer ====
@router.callback_query(F.data == "stop_timer")
async def stop_timer(callback: CallbackQuery):
    user_id = callback.from_user.id
    timer = timers.get(user_id)

    if not timer:
        await callback.answer("⚠️ No active timer.", show_alert=True)
        return

    if timer.task:
        timer.task.cancel()
    del timers[user_id]
    settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}

    await callback.message.answer(
        "⏹ Timer stopped.\n\n🔄 Want to start a new one?",
        reply_markup=build_timer_keyboard(user_id)
    )
    await callback.answer()

# ==== No-op ====
@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()