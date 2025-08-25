import pytest
from unittest.mock import AsyncMock, patch
from src.services.wger_service import fetch_wger_exercises, sync_wger_exercises
from src.models.exercise import Exercise
from src.data.seed_exercises import seed_exercises
from sqlalchemy import select

@pytest.mark.asyncio
async def test_fetch_wger_exercises():
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'results': [
                {
                    'name': 'Axe Hold',
                    'category': {'name': 'Arms'},
                    'muscles': [{'name': 'Biceps'}],
                    'equipment': [{'name': 'Axe'}]
                }
            ]
        })
        mock_get.return_value.__aenter__.return_value = mock_response
        exercises = await fetch_wger_exercises()
        assert len(exercises) == 1
        assert exercises[0]['name'] == 'Axe Hold'
        assert exercises[0]['equipment'] == 'Axe'

@pytest.mark.asyncio
async def test_fetch_wger_exercises_error():
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response
        exercises = await fetch_wger_exercises()
        assert len(exercises) == 0

@pytest.mark.asyncio
async def test_sync_wger_exercises(test_db):
    await seed_exercises(test_db)
    with patch('src.services.wger_service.fetch_wger_exercises') as mock_fetch:
        mock_fetch.return_value = [
            {
                'name': 'Axe Hold',
                'category': 'Arms',
                'primary_muscle': 'Biceps',
                'equipment': 'Axe'
            }
        ]
        await sync_wger_exercises(test_db)
        result = (await test_db.execute(select(Exercise).where(Exercise.name == 'Axe Hold'))).scalars().first()
        assert result is not None
        assert result.name == 'Axe Hold'
        assert result.equipment == 'Axe'@pytest.mark.asyncio
async def test_fetch_wger_exercises_limit():
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'results': [
                {
                    'name': 'Push-up',
                    'category': {'name': 'Chest'},
                    'muscles': [{'name': 'Pectorals'}],
                    'equipment': []
                }
            ]
        })
        mock_get.return_value.__aenter__.return_value = mock_response
        exercises = await fetch_wger_exercises(limit=1)
        assert len(exercises) == 1
        assert exercises[0]['name'] == 'Push-up'
        assert exercises[0]['equipment'] == ''
        mock_get.assert_called_with('https://wger.de/api/v2/exerciseinfo/', params={'limit': 1})