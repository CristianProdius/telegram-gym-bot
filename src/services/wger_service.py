import aiohttp
import logging

logger = logging.getLogger(__name__)

async def fetch_wger_exercises(session: aiohttp.ClientSession, category: str = None, limit: int = 10):
    '''Fetch exercises from Wger API.'''
    url = 'https://wger.de/api/v2/exercise/'
    params = {'limit': limit, 'language': 2}  # language=2 for English
    if category:
        params['category'] = category
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('results', [])
            else:
                logger.error(f'Wger API error: {response.status}')
                return []
    except aiohttp.ClientError as e:
        logger.error(f'Wger API request failed: {e}')
        return []
