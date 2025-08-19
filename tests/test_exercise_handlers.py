import pytest
from src.data.seed_exercises import seed_exercises
from src.handlers.exercise_handlers import get_exercise_page, format_exercise

@pytest.mark.asyncio
async def test_format_exercise(test_db):
    seed_exercises(test_db)
    ex = test_db.query(type(seed_exercises.INITIAL_EXERCISES[0])).first()
    text = format_exercise(ex)
    assert "Категория" in text
    assert "Мышца" in text

@pytest.mark.asyncio
async def test_get_categories(test_db):
    seed_exercises(test_db)
    categories = sorted(set(ex.category for ex in test_db.query(type(seed_exercises.INITIAL_EXERCISES[0])).all()))
    assert "Chest" in categories
