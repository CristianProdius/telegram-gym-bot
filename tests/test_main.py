import pytest
from aiogram import Dispatcher, Bot
from aiogram.types import User
from src.main import main
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_main():
    with patch('aiogram.Bot') as mock_bot, \
         patch('aiogram.Dispatcher') as mock_dp, \
         patch('sqlalchemy.ext.asyncio.create_async_engine') as mock_engine, \
         patch('sqlalchemy.orm.sessionmaker') as mock_sessionmaker, \
         patch('os.getenv') as mock_getenv:
        mock_getenv.return_value = '123456:ABC-DEF1234ghIkl-xyz'
        mock_bot_instance = AsyncMock()
        mock_bot.return_value = mock_bot_instance
        mock_bot_instance.me = AsyncMock(return_value=User(id=123456, is_bot=True, first_name='TestBot'))
        mock_dp_instance = AsyncMock()
        mock_dp.return_value = mock_dp_instance
        mock_session = AsyncMock()
        mock_sessionmaker.return_value.__aenter__.return_value = mock_session
        await main()
        mock_bot.assert_called_once_with(token='123456:ABC-DEF1234ghIkl-xyz')
        mock_bot_instance.me.assert_called_once()
        mock_dp.assert_called_once()
        mock_engine.assert_called_once_with('sqlite+aiosqlite:///:memory:', echo=False)
        mock_sessionmaker.assert_called_once()
        mock_dp_instance.include_router.assert_called_once()
        mock_dp_instance.start_polling.assert_called_once()