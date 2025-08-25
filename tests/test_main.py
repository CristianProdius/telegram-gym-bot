import pytest
from aiogram import Dispatcher, Bot
from src.main import register_handlers, main
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_register_handlers():
    dp = Dispatcher()
    register_handlers(dp)
    assert len(dp.message.handlers) > 0

@pytest.mark.asyncio
async def test_main():
    with patch('aiogram.Bot') as mock_bot, patch('aiogram.Dispatcher') as mock_dp, \
         patch('src.main.register_handlers') as mock_register, \
         patch('aiogram.Dispatcher.start_polling') as mock_polling:
        mock_dp_instance = AsyncMock()
        mock_dp.return_value = mock_dp_instance
        await main()
        mock_bot.assert_called_once()
        mock_dp.assert_called_once()
        mock_register.assert_called_once_with(mock_dp_instance)
        mock_polling.assert_called_once()