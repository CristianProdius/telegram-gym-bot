import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from src.services.notification_service import notification_service
from src.services.nutrition_service import nutrition_service

from src.bot.config import config
from src.handlers import register_all_handlers
from src.database.connection import init_db, close_db

logger = logging.getLogger(__name__)

class GymBot:
    """Main bot application class"""

    def __init__(self):
        self.bot = Bot(
            token=config.TELEGRAM_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging"""
        log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('bot.log', encoding='utf-8')
            ]
        )

    async def on_startup(self):
        """Actions to perform on bot startup"""
        logger.info("Starting bot...")

        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Seed exercises
        from src.data.exercises import seed_exercises
        from src.database.connection import get_session
        async with get_session() as session:
            count = await seed_exercises(session)
            logger.info(f"Seeded {count} exercises to database")

        # Register handlers
        register_all_handlers(self.dp)
        logger.info("Handlers registered")

        # Start background tasks
        from src.services.timer_service import timer_manager
        timer_manager.start_cleanup_task()
        logger.info("Background tasks started")

        # Initialize notification service
        notification_service.set_bot(self.bot)
        await notification_service.initialize_all_notifications()
        logger.info("Notification service initialized")

        # Initialize nutrition service HTTP session
        await nutrition_service.create_session()
        logger.info("Nutrition service initialized")

        logger.info("Bot startup complete!")

    async def on_shutdown(self):
        """Actions to perform on bot shutdown"""
        logger.info("Shutting down bot...")
        
        # Shutdown nutrition service HTTP session
        await nutrition_service.close_session()
        logger.info("Nutrition service session closed")
        
        # Shutdown notification service
        notification_service.shutdown()
        logger.info("Notification service shutdown")

        # Cleanup timers
        from src.services.timer_service import timer_manager
        timer_manager.shutdown()
        logger.info("Timer service shutdown")

        # Close database
        await close_db()
        logger.info("Database connection closed")

        # Close bot session
        await self.bot.session.close()
        logger.info("Bot session closed")
        
        logger.info("Bot shutdown complete")

    async def start_polling(self):
        """Start bot in polling mode"""
        try:
            await self.on_startup()
            logger.info("Starting polling...")
            await self.dp.start_polling(self.bot)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise
        finally:
            await self.on_shutdown()

    async def start_webhook(self):
        """Start bot in webhook mode"""
        if not config.WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL not configured")

        # TODO: Implement webhook mode
        raise NotImplementedError("Webhook mode not implemented yet")

def create_bot() -> GymBot:
    """Factory function to create bot instance"""
    return GymBot()

# Main entry point
async def main():
    """Main entry point for the bot"""
    # Validate configuration before starting
    if not config.validate():
        logger.error("Configuration validation failed!")
        return

    # Create and start bot
    bot = create_bot()
    
    if config.IS_PRODUCTION and config.WEBHOOK_URL:
        logger.info("Starting in webhook mode")
        await bot.start_webhook()
    else:
        logger.info("Starting in polling mode")
        await bot.start_polling()

if __name__ == "__main__":
    asyncio.run(main())