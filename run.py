#!/usr/bin/env python3
"""
Main entry point for the Telegram Gym Bot
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.bot.app import create_bot
from src.bot.config import config

logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot"""
    # Validate configuration
    if not config.validate():
        logger.error("Invalid configuration. Exiting...")
        sys.exit(1)

    # Create and start bot
    bot = create_bot()

    if config.IS_PRODUCTION and config.WEBHOOK_URL:
        await bot.start_webhook()
    else:
        await bot.start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)