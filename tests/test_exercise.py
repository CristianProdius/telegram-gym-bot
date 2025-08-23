import pytest
from src.models.exercise import Exercise
from src.data.seed_exercises import seed_exercises, INITIAL_EXERCISES
from src.services.exercise_service import list_exercises, find_exercises_by_name
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_exercise_model_creation(test_db):
    exercise = Exercise(name='Bench Press', category='Chest', primary_muscle='Pectorals')
    test_db.add(exercise)
    await test_db.commit()
    saved = (await test_db.execute(select(Exercise))).scalars().first()
    assert saved.name == 'Bench Press'
    assert saved.category == 'Chest'

@pytest.mark.asyncio
async def test_seed_exercises(test_db):
    await seed_exercises(test_db)
    exercises = await list_exercises(test_db)
    assert len(exercises) == len(INITIAL_EXERCISES)

@pytest.mark.asyncio
async def test_find_exercises_by_name(test_db):
    await seed_exercises(test_db)
    results = await find_exercises_by_name(test_db, 'squat')
    assert any('Squat' in e.name for e in results)
