import pytest
from aiogram import Bot, Dispatcher
from aiogram.types import Message, User, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, patch
from src.handlers.exercise_handlers import get_exercise_page, format_exercise, cmd_exercises, cmd_start, search_exercise
from src.models.exercise import Exercise
from src.data.seed_exercises import seed_exercises
from sqlalchemy import select

@pytest.mark.asyncio
async def test_format_exercise(test_db):
    await seed_exercises(test_db)
    ex = (await test_db.execute(select(Exercise))).scalars().first()
    text = format_exercise(ex)
    assert 'Категория' in text
    assert 'Pectorals' in text
    assert 'Оборудование' in text

@pytest.mark.asyncio
async def test_get_exercise_page(test_db):
    await seed_exercises(test_db)
    text, keyboard = await get_exercise_page(test_db, page=0)
    assert 'Bench Press' in text
    assert len(keyboard.inline_keyboard) <= 1

@pytest.mark.asyncio
async def test_get_exercise_page_empty(test_db):
    text, keyboard = await get_exercise_page(test_db, page=0)
    assert text == 'Упражнения не найдены.'
    assert isinstance(keyboard, InlineKeyboardMarkup)

@pytest.mark.asyncio
async def test_get_exercise_page_pagination(test_db):
    await seed_exercises(test_db)
    for i in range(10):
        exercise = Exercise(name=f'Test Exercise {i}', category='Test', primary_muscle='Test Muscle', equipment='Dumbbell')
        test_db.add(exercise)
    await test_db.commit()
    text, keyboard = await get_exercise_page(test_db, page=1)
    assert len(keyboard.inline_keyboard) > 0
    assert any('Назад' in button.text for row in keyboard.inline_keyboard for button in row)
    assert any('Вперёд' in button.text for row in keyboard.inline_keyboard for button in row)

@pytest.mark.asyncio
async def test_cmd_exercises(test_db):
    await seed_exercises(test_db)
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=User)
    message.from_user.id = 123
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    await cmd_exercises(message, state=state, session=test_db)
    message.answer.assert_called()
    assert 'Bench Press' in message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_search_exercise_valid_input(test_db):
    await seed_exercises(test_db)
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=User)
    message.from_user.id = 123
    message.text = '/search_exercise Squat'
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    await search_exercise(message, state=state, session=test_db)
    message.answer.assert_called_with('Squat — Quadriceps\nКатегория: Legs\nОборудование: Barbell')

@pytest.mark.asyncio
async def test_search_exercise_invalid_input(test_db):
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=User)
    message.from_user.id = 123
    message.text = '/search_exercise 12!'
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    await search_exercise(message, state=state, session=test_db)
    message.answer.assert_called_with('Некорректный запрос. Используйте: /search_exercise <название>, только буквы и пробелы, минимум 2 символа.')

@pytest.mark.asyncio
async def test_search_exercise_no_query(test_db):
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=User)
    message.from_user.id = 123
    message.text = '/search_exercise'
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    await search_exercise(message, state=state, session=test_db)
    message.answer.assert_called_with('Некорректный запрос. Используйте: /search_exercise <название>, только буквы и пробелы, минимум 2 символа.')

@pytest.mark.asyncio
async def test_cmd_start():
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=User)
    message.from_user.id = 123
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    await cmd_start(message, state=state)
    message.answer.assert_called_with('Привет! Это бот для упражнений. Используй команды:\n'
                                     '/exercises - Список упражнений\n'
                                     '/search_exercise <название> - Поиск упражнения')