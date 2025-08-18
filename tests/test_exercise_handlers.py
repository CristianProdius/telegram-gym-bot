import pytest
from aiogram.types import Message
from src.data.seed_exercises import seed_exercises
from src.services.exercise_service import list_exercises
from src.handlers.exercise_handlers import get_exercise_page

@pytest.mark.asyncio
async def test_get_exercise_page(test_db):
    seed_exercises(test_db)
    text, keyboard = get_exercise_page(test_db, page=0)
    assert "Bench Press" in text
    assert keyboard.inline_keyboard is not None

@pytest.mark.asyncio
async def test_search_exercise_found(test_db):
    seed_exercises(test_db)
    results = list_exercises(test_db)
    assert any("Squat" in e.name for e in results)

