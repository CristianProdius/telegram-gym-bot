from src.models.exercise import Exercise
from sqlalchemy.ext.asyncio import AsyncSession

INITIAL_EXERCISES = [
    {'name': 'Bench Press', 'category': 'Chest', 'primary_muscle': 'Pectorals'},
    {'name': 'Squat', 'category': 'Legs', 'primary_muscle': 'Quadriceps'},
    {'name': 'Deadlift', 'category': 'Back', 'primary_muscle': 'Erector Spinae'},
    {'name': 'Overhead Press', 'category': 'Shoulders', 'primary_muscle': 'Deltoids'},
    {'name': 'Pull-Up', 'category': 'Back', 'primary_muscle': 'Latissimus Dorsi'},
]

async def seed_exercises(session: AsyncSession):
    async with session.begin():
        for exercise_data in INITIAL_EXERCISES:
            exercise = Exercise(**exercise_data)
            session.add(exercise)
