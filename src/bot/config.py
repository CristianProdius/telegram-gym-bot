import os
from typing import Optional
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """Bot configuration management"""

    # Bot settings
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///main/gymbot.db")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    IS_PRODUCTION: bool = ENVIRONMENT == "production"
    IS_DEVELOPMENT: bool = ENVIRONMENT == "development"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Rate limiting
    MAX_CONCURRENT_USERS: int = int(os.getenv("MAX_CONCURRENT_USERS", "100"))
    RATE_LIMIT_MESSAGES_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_MESSAGES_PER_MINUTE", "20"))

    # Webhook (for production)
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "8443"))

    # Redis (optional)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # Admin
    ADMIN_USER_IDS: list[int] = [
        int(uid.strip())
        for uid in os.getenv("ADMIN_USER_IDS", "").split(",")
        if uid.strip()
    ]

    # Feature flags
    ENABLE_NUTRITION: bool = os.getenv("ENABLE_NUTRITION", "False").lower() == "true"
    ENABLE_SOCIAL: bool = os.getenv("ENABLE_SOCIAL", "False").lower() == "true"
    ENABLE_AI_RECOMMENDATIONS: bool = os.getenv("ENABLE_AI_RECOMMENDATIONS", "False").lower() == "true"

    # Limits
    MAX_WORKOUTS_PER_DAY: int = int(os.getenv("MAX_WORKOUTS_PER_DAY", "10"))
    MAX_EXERCISES_PER_WORKOUT: int = int(os.getenv("MAX_EXERCISES_PER_WORKOUT", "50"))

    # Notifications
    ENABLE_NOTIFICATIONS: bool = os.getenv("ENABLE_NOTIFICATIONS", "True").lower() == "true"
    REMINDER_TIME: str = os.getenv("REMINDER_TIME", "09:00")

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.TELEGRAM_TOKEN:
            logger.error("TELEGRAM_TOKEN is not set!")
            return False

        if cls.IS_PRODUCTION and not cls.WEBHOOK_URL:
            logger.warning("Running in production without webhook URL")

        return True

config = Config()