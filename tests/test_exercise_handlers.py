import pytest
from src.data.seed_exercises import seed_exercises
from src.handlers.exercise_handlers import get_exercise_page, format_exercise
from src.models.exercise import Exercise
from sqlalchemy.future import select
from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_format_exercise(test_db):
    await seed_exercises(test_db)
    ex = (await test_db.execute(select(Exercise))).scalars().first()
    text = format_exercise(ex)
    assert 'Категория' in text
    assert 'Мышца' in text

@pytest.mark.asyncio
async def test_get_exercise_page(test_db):
    await seed_exercises(test_db)
    text, keyboard = get_exercise_page(test_db, page=0)
    assert 'Bench Press' in text
    assert len(keyboard.inline_keyboard) <= 1

@pytest.mark.asyncio
async def test_search_exercise_valid_input(test_db):
    dp = Dispatcher()
    bot = AsyncMock(spec=Bot)
    message = AsyncMock(spec=Message)
    state = AsyncMock(spec=FSMContext)
    message.text = 'Squat'
    message.from_user.id = 123
    await dp.message.handlers[0].handlers[4].handler(message, state=state, session=test_db)
    message.answer.assert_called_with('Squat — Quadriceps')

@pytest.mark.asyncio
async def test_search_exercise_invalid_input(test_db):
    dp = Dispatcher()
    bot = AsyncMock(spec=Bot)
    message = AsyncMock(spec=Message)
    state = AsyncMock(spec=FSMContext)
    message.text = '12!'
    message.from_user.id = 123
    await dp.message.handlers[0].handlers[4].handler(message, state=state, session=test_db)
    message.answer.assert_called_with('Некорректный запрос. Используйте только буквы и пробелы, минимум 2 символа.')
