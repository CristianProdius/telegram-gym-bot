"""Pytest configuration and fixtures"""

import pytest
import asyncio
from typing import AsyncGenerator
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from faker import Faker

from src.database.connection import Base
from src.models import User, Exercise, Workout, WorkoutExercise, WorkoutSet, Routine

fake = Faker()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db():
    """Create a test database for each test function"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()

@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        telegram_id=fake.random_int(min=100000, max=999999),
        username=fake.user_name(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        created_at=datetime.now(),
        last_active=datetime.now(),
        is_active=True,
        language_code="en",
        weight_unit="kg",
        timezone="UTC"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user

@pytest.fixture
async def test_exercises(test_db: AsyncSession) -> list[Exercise]:
    """Create test exercises"""
    exercises = [
        Exercise(
            name="Bench Press",
            category="Chest",
            muscle_group="Pectorals",
            equipment="Barbell"
        ),
        Exercise(
            name="Squat",
            category="Legs",
            muscle_group="Quadriceps",
            equipment="Barbell"
        ),
        Exercise(
            name="Deadlift",
            category="Back",
            muscle_group="Erector Spinae",
            equipment="Barbell"
        ),
        Exercise(
            name="Pull-ups",
            category="Back",
            muscle_group="Latissimus Dorsi",
            equipment="Bodyweight"
        ),
        Exercise(
            name="Overhead Press",
            category="Shoulders",
            muscle_group="Deltoids",
            equipment="Barbell"
        )
    ]

    for exercise in exercises:
        test_db.add(exercise)

    await test_db.commit()

    for exercise in exercises:
        await test_db.refresh(exercise)

    return exercises

@pytest.fixture
async def test_workout(test_db: AsyncSession, test_user: User, test_exercises: list[Exercise]) -> Workout:
    """Create a test workout with exercises and sets"""
    workout = Workout(
        user_id=test_user.id,
        date=datetime.now()
    )
    test_db.add(workout)
    await test_db.flush()

    # Add workout exercise
    workout_exercise = WorkoutExercise(
        workout_id=workout.id,
        exercise_id=test_exercises[0].id,  # Bench Press
        order=0
    )
    test_db.add(workout_exercise)
    await test_db.flush()

    # Add sets
    for i in range(1, 4):
        workout_set = WorkoutSet(
            workout_exercise_id=workout_exercise.id,
            set_number=i,
            reps=10,
            weight=60.0 + (i * 2.5),
            rest_seconds=90
        )
        test_db.add(workout_set)

    await test_db.commit()
    await test_db.refresh(workout)
    return workout

@pytest.fixture
async def test_routine(test_db: AsyncSession, test_user: User, test_exercises: list[Exercise]) -> Routine:
    """Create a test routine"""
    routine = Routine(
        user_id=test_user.id,
        name="Test PPL Routine",
        description="A test push-pull-legs routine",
        category="PPL",
        difficulty="intermediate",
        is_public=False
    )
    test_db.add(routine)
    await test_db.commit()
    await test_db.refresh(routine)
    return routine

@pytest.fixture
def mock_telegram_update():
    """Create a mock Telegram update object"""
    class MockUser:
        def __init__(self):
            self.id = fake.random_int(min=100000, max=999999)
            self.username = fake.user_name()
            self.first_name = fake.first_name()
            self.last_name = fake.last_name()

    class MockMessage:
        def __init__(self):
            self.from_user = MockUser()
            self.text = "/start"
            self.date = datetime.now()

        async def answer(self, text, **kwargs):
            return {"text": text, "kwargs": kwargs}

        async def edit_text(self, text, **kwargs):
            return {"text": text, "kwargs": kwargs}

    class MockCallbackQuery:
        def __init__(self, data=""):
            self.from_user = MockUser()
            self.data = data
            self.message = MockMessage()

        async def answer(self, text=None, **kwargs):
            return {"text": text, "kwargs": kwargs}

    class MockUpdate:
        def __init__(self):
            self.message = MockMessage()
            self.callback_query = None

    return MockUpdate()