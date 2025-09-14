import asyncio
import weakref
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Timer:
    def __init__(self, duration_seconds: int):
        self.duration = duration_seconds
        self.start_time = None
        self.task: Optional[asyncio.Task] = None

    def start(self):
        self.start_time = datetime.now()

    def remaining_seconds(self) -> int:
        if not self.start_time:
            return self.duration
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return max(0, self.duration - int(elapsed))

    def cancel(self):
        """Cancel the timer and cleanup resources"""
        if self.task and not self.task.done():
            self.task.cancel()
            self.task = None

class TimerManager:
    """Manages timers with automatic cleanup and memory management"""

    def __init__(self):
        self.timers: Dict[int, Timer] = {}
        self.settings: Dict[int, dict] = {}
        self._cleanup_task = None

    def start_cleanup_task(self):
        """Start periodic cleanup of expired timers"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def _periodic_cleanup(self):
        """Periodically clean up expired timers and settings"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                self.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in timer cleanup: {e}")

    def cleanup_expired(self):
        """Remove expired timers and old settings"""
        expired_users = []
        for user_id, timer in self.timers.items():
            if timer.task and timer.task.done():
                expired_users.append(user_id)

        for user_id in expired_users:
            self.remove_timer(user_id)
            logger.debug(f"Cleaned up expired timer for user {user_id}")

    def add_timer(self, user_id: int, timer: Timer) -> None:
        """Add a timer for a user"""
        # Cancel existing timer if present
        if user_id in self.timers:
            self.remove_timer(user_id)
        self.timers[user_id] = timer

    def get_timer(self, user_id: int) -> Optional[Timer]:
        """Get timer for a user"""
        return self.timers.get(user_id)

    def remove_timer(self, user_id: int) -> None:
        """Remove and cleanup timer for a user"""
        if user_id in self.timers:
            timer = self.timers[user_id]
            timer.cancel()
            del self.timers[user_id]

    def get_settings(self, user_id: int) -> dict:
        """Get or create settings for a user"""
        if user_id not in self.settings:
            self.settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}
        return self.settings[user_id]

    def clear_settings(self, user_id: int) -> None:
        """Clear settings for a user"""
        if user_id in self.settings:
            del self.settings[user_id]

    def shutdown(self):
        """Cleanup all resources on shutdown"""
        # Cancel all active timers
        for user_id in list(self.timers.keys()):
            self.remove_timer(user_id)

        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

        # Clear all data
        self.timers.clear()
        self.settings.clear()
        logger.info("Timer manager shutdown complete")

# Create global timer manager instance
timer_manager = TimerManager()