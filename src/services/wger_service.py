import aiohttp
from typing import List, Dict, Any
from src.models.exercise import Exercise
from sqlalchemy.ext.asyncio import AsyncSession

async def fetch_wger_exercises(limit: int = None) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        params = {'limit': limit} if limit else {}
        async with session.get('https://wger.de/api/v2/exerciseinfo/', params=params) as response:
            if response.status == 200:
                data = await response.json()
                exercises = []
                for item in data.get('results', []):
                    equipment = ','.join([eq['name'] for eq in item.get('equipment', [])])
                    exercise = {
                        'name': item.get('name', ''),
                        'category': item.get('category', {}).get('name', ''),
                        'primary_muscle': item.get('muscles', [{}])[0].get('name', ''),
                        'equipment': equipment
                    }
                    exercises.append(exercise)
                return exercises
            return []

async def sync_wger_exercises(session: AsyncSession) -> None:
    exercises_data = await fetch_wger_exercises()
    for ex_data in exercises_data:
        exercise = Exercise(**ex_data)
        session.add(exercise)
    await session.commit()