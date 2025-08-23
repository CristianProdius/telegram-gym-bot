import pytest
import aiohttp
from src.services.wger_service import fetch_wger_exercises

@pytest.mark.asyncio
async def test_fetch_wger_exercises_success():
    async with aiohttp.ClientSession() as session:
        exercises = await fetch_wger_exercises(session, limit=2)
        assert isinstance(exercises, list)
        assert len(exercises) > 0
        assert 'name' in exercises[0]
        assert 'category' in exercises[0]

@pytest.mark.asyncio
async def test_fetch_wger_exercises_empty():
    async with aiohttp.ClientSession() as session:
        exercises = await fetch_wger_exercises(session, category='Nonexistent')
        assert exercises == []
