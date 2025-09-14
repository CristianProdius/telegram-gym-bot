import logging
from aiogram import Router, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.services.timer_service import timer_manager, Timer
from src.utils.keyboards import build_timer_keyboard

logger = logging.getLogger(__name__)

def register_timer_handlers(dp: Dispatcher):
    """Register timer handlers"""
    router = Router()

    async def refresh_config_message(callback: CallbackQuery, user_id: int):
        """Refresh timer configuration message"""
        await callback.message.edit_text(
            "⏱ Настройте таймер отдыха:",
            reply_markup=build_timer_keyboard(user_id)
        )

    @router.message(Command("timer"))
    async def cmd_timer(message: Message):
        """Handle /timer command"""
        user_id = message.from_user.id
        timer_manager.get_settings(user_id)  # Initialize settings
        await message.answer(
            "⏱ Настройте таймер отдыха:",
            reply_markup=build_timer_keyboard(user_id)
        )
        logger.info(f"User {user_id} opened timer settings")

    # Timer adjustment handlers
    @router.callback_query(F.data == "add_hour")
    async def add_hour(callback: CallbackQuery):
        user_id = callback.from_user.id
        settings = timer_manager.get_settings(user_id)
        settings["hours"] += 1
        await refresh_config_message(callback, user_id)
        await callback.answer("➕ 1 час")

    @router.callback_query(F.data == "add_minute")
    async def add_minute(callback: CallbackQuery):
        user_id = callback.from_user.id
        settings = timer_manager.get_settings(user_id)
        if settings["minutes"] < 59:
            settings["minutes"] += 1
        else:
            settings["minutes"] = 0
            settings["hours"] += 1
        await refresh_config_message(callback, user_id)
        await callback.answer("➕ 1 минута")

    @router.callback_query(F.data == "add_second")
    async def add_second(callback: CallbackQuery):
        user_id = callback.from_user.id
        settings = timer_manager.get_settings(user_id)
        if settings["seconds"] < 59:
            settings["seconds"] += 1
        else:
            settings["seconds"] = 0
            if settings["minutes"] < 59:
                settings["minutes"] += 1
            else:
                settings["minutes"] = 0
                settings["hours"] += 1
        await refresh_config_message(callback, user_id)
        await callback.answer("➕ 1 секунда")

    @router.callback_query(F.data == "sub_hour")
    async def sub_hour(callback: CallbackQuery):
        user_id = callback.from_user.id
        settings = timer_manager.get_settings(user_id)
        if settings["hours"] > 0:
            settings["hours"] -= 1
        await refresh_config_message(callback, user_id)
        await callback.answer("➖ 1 час")

    @router.callback_query(F.data == "sub_minute")
    async def sub_minute(callback: CallbackQuery):
        user_id = callback.from_user.id
        settings = timer_manager.get_settings(user_id)
        if settings["minutes"] > 0:
            settings["minutes"] -= 1
        elif settings["hours"] > 0:
            settings["hours"] -= 1
            settings["minutes"] = 59
        await refresh_config_message(callback, user_id)
        await callback.answer("➖ 1 минута")

    @router.callback_query(F.data == "sub_second")
    async def sub_second(callback: CallbackQuery):
        user_id = callback.from_user.id
        settings = timer_manager.get_settings(user_id)
        if settings["seconds"] > 0:
            settings["seconds"] -= 1
        elif settings["minutes"] > 0:
            settings["minutes"] -= 1
            settings["seconds"] = 59
        elif settings["hours"] > 0:
            settings["hours"] -= 1
            settings["minutes"] = 59
            settings["seconds"] = 59
        await refresh_config_message(callback, user_id)
        await callback.answer("➖ 1 секунда")

    @router.callback_query(F.data == "start_timer")
    async def start_timer(callback: CallbackQuery):
        """Start timer"""
        import asyncio
        user_id = callback.from_user.id
        s = timer_manager.get_settings(user_id)
        total_seconds = s["hours"] * 3600 + s["minutes"] * 60 + s["seconds"]

        if total_seconds <= 0:
            await callback.answer("⚠️ Время не установлено", show_alert=True)
            return

        timer = Timer(total_seconds)
        timer.start()
        timer_manager.add_timer(user_id, timer)

        async def notify():
            try:
                await asyncio.sleep(total_seconds)
                current_timer = timer_manager.get_timer(user_id)
                if current_timer == timer:
                    timer_manager.remove_timer(user_id)
                    timer_manager.settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}
                    await callback.message.answer(
                        "✅ Таймер завершен!\n\n🔄 Хотите установить новый?",
                        reply_markup=build_timer_keyboard(user_id)
                    )
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Timer notification error: {e}")

        timer.task = asyncio.create_task(notify())
        await callback.message.answer(f"⏳ Таймер на {total_seconds} секунд запущен!")
        await callback.answer()
        logger.info(f"User {user_id} started timer for {total_seconds} seconds")

    @router.callback_query(F.data == "stop_timer")
    async def stop_timer(callback: CallbackQuery):
        """Stop timer"""
        user_id = callback.from_user.id
        timer = timer_manager.get_timer(user_id)

        if not timer:
            await callback.answer("⚠️ Нет активного таймера", show_alert=True)
            return

        timer_manager.remove_timer(user_id)
        timer_manager.settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}

        await callback.message.answer(
            "⏹ Таймер остановлен.\n\n🔄 Хотите установить новый?",
            reply_markup=build_timer_keyboard(user_id)
        )
        await callback.answer()
        logger.info(f"User {user_id} stopped timer")

    @router.callback_query(F.data == "noop")
    async def noop(callback: CallbackQuery):
        """No-op handler for display-only buttons"""
        await callback.answer()

    dp.include_router(router)