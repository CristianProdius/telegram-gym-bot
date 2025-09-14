"""Integration tests for bot handlers"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from src.handlers.workout import register_workout_handlers, WorkoutStates
from src.handlers.start import register_start_handlers
from src.handlers.timer import register_timer_handlers

@pytest.mark.asyncio
class TestBotHandlers:
    """Test bot handler integration"""

    async def test_start_command(self, mock_telegram_update):
        """Test /start command handler"""
        message = mock_telegram_update.message
        message.text = "/start"

        # Mock the answer method
        answer_mock = AsyncMock()
        message.answer = answer_mock

        # Import handler function directly
        from src.handlers.start import cmd_start

        await cmd_start(message)

        # Check that welcome message was sent
        answer_mock.assert_called_once()
        call_args = answer_mock.call_args[0][0]
        assert "Gym Bot" in call_args
        assert "помощник" in call_args or "assistant" in call_args

    async def test_help_command(self, mock_telegram_update):
        """Test /help command handler"""
        message = mock_telegram_update.message
        message.text = "/help"

        answer_mock = AsyncMock()
        message.answer = answer_mock

        from src.handlers.start import cmd_help

        await cmd_help(message)

        answer_mock.assert_called_once()
        call_args = answer_mock.call_args[0][0]
        assert "/log" in call_args
        assert "/timer" in call_args

    async def test_workout_log_start(self, mock_telegram_update, test_exercises):
        """Test starting workout log conversation"""
        message = mock_telegram_update.message
        message.text = "/log"

        # Create FSM context
        storage = MemoryStorage()
        state = FSMContext(storage=storage, key=storage.get_key(
            bot_id=1,
            chat_id=message.from_user.id,
            user_id=message.from_user.id
        ))

        answer_mock = AsyncMock()
        message.answer = answer_mock

        from src.handlers.workout import cmd_log_workout

        await cmd_log_workout(message, state)

        # Check state was set
        current_state = await state.get_state()
        assert current_state == WorkoutStates.selecting_exercise.state

        # Check exercise keyboard was sent
        answer_mock.assert_called_once()

    async def test_timer_command(self, mock_telegram_update):
        """Test /timer command handler"""
        message = mock_telegram_update.message
        message.text = "/timer"

        answer_mock = AsyncMock()
        message.answer = answer_mock

        from src.handlers.timer import cmd_timer

        await cmd_timer(message)

        answer_mock.assert_called_once()
        call_args = answer_mock.call_args
        assert "reply_markup" in call_args[1]

    async def test_timer_adjustment(self, mock_telegram_update):
        """Test timer adjustment callbacks"""
        from src.handlers.timer import add_hour, add_minute, add_second

        # Create callback query
        callback = mock_telegram_update.callback_query
        if not callback:
            from tests.conftest import MockCallbackQuery
            callback = MockCallbackQuery(data="add_hour")
            mock_telegram_update.callback_query = callback

        answer_mock = AsyncMock()
        edit_mock = AsyncMock()
        callback.answer = answer_mock
        callback.message.edit_text = edit_mock

        # Test adding hour
        await add_hour(callback)

        answer_mock.assert_called_once()
        edit_mock.assert_called_once()

    async def test_workout_flow_integration(self, test_db, test_user, test_exercises):
        """Test complete workout logging flow"""
        from src.services.workout_service import WorkoutService

        service = WorkoutService()

        # Log a workout
        workout = await service.log_workout_sets(
            user_id=test_user.id,
            exercise_id=test_exercises[0].id,
            sets=[
                {"reps": 10, "weight": 60},
                {"reps": 8, "weight": 65},
                {"reps": 6, "weight": 70}
            ]
        )

        assert workout is not None

        # Get today's workouts
        today_workouts = await service.get_today_workouts(test_user.id)

        assert len(today_workouts) > 0
        assert today_workouts[0]["exercise"] == test_exercises[0].name

        # Get statistics
        stats = await service.get_user_statistics(test_user.id)

        assert stats["total_workouts"] == 1
        assert stats["total_volume"] > 0

    async def test_language_switching(self, mock_telegram_update):
        """Test language switching functionality"""
        from src.locales.translations import i18n

        user_id = mock_telegram_update.message.from_user.id

        # Default should be English
        message = i18n.get("welcome", user_id)
        assert "Welcome" in message or "welcome" in message.lower()

        # Switch to Russian
        i18n.set_user_language(user_id, "ru")
        message = i18n.get("welcome", user_id)
        assert "Добро пожаловать" in message or "Привет" in message

        # Switch back to English
        i18n.set_user_language(user_id, "en")
        message = i18n.get("welcome", user_id)
        assert "Welcome" in message or "welcome" in message.lower()