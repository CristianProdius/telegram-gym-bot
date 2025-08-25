from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.exercise import Exercise

async def list_exercises(session: AsyncSession) -> List[Exercise]:
    result = await session.execute(select(Exercise))
    return result.scalars().all()

async def find_exercises_by_name(session: AsyncSession, name: str) -> List[Exercise]:
    result = await session.execute(select(Exercise).where(Exercise.name.ilike(f'%{name}%')))
    return result.scalars().all()