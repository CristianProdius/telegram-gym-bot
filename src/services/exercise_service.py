from sqlalchemy.ext.asyncio import AsyncSession
from src.models.exercise import Exercise
from sqlalchemy.future import select

async def list_exercises(session: AsyncSession):
    result = await session.execute(select(Exercise))
    return result.scalars().all()

async def find_exercises_by_name(session: AsyncSession, query: str):
    result = await session.execute(
        select(Exercise).filter(Exercise.name.ilike(f'%{query}%'))
    )
    return result.scalars().all()
