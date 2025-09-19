"""Notification service for managing training reminders"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from aiogram import Bot

from src.models.notification import TrainingNotification
from src.models.user import User

class NotificationService:
    """Service for managing training notifications"""
    
    def __init__(self):
        self.active_tasks: Dict[int, List[asyncio.Task]] = {}
        self.bot: Optional[Bot] = None
    
    def set_bot(self, bot: Bot):
        """Set bot instance for sending messages"""
        self.bot = bot
    
    async def add_notification(
        self,
        session: AsyncSession,
        user_id: int,
        weekday: int,
        training_time: time
    ) -> TrainingNotification:
        """Add a new training notification"""
        notification = TrainingNotification(
            user_id=user_id,
            weekday=weekday,
            training_time=training_time
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        
        # Start reminder task
        await self._start_reminder_task(notification)
        
        return notification
    
    async def get_user_notifications(
        self,
        session: AsyncSession,
        user_id: int
    ) -> List[TrainingNotification]:
        """Get all notifications for a user"""
        stmt = select(TrainingNotification).where(
            TrainingNotification.user_id == user_id,
            TrainingNotification.is_active == True
        ).order_by(TrainingNotification.weekday, TrainingNotification.training_time)
        
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def update_notification(
        self,
        session: AsyncSession,
        notification_id: int,
        weekday: int,
        training_time: time
    ) -> Optional[TrainingNotification]:
        """Update an existing notification"""
        stmt = select(TrainingNotification).where(TrainingNotification.id == notification_id)
        result = await session.execute(stmt)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return None
        
        # Cancel old task
        await self._cancel_user_tasks(notification.user_id)
        
        # Update notification
        notification.weekday = weekday
        notification.training_time = training_time
        await session.commit()
        await session.refresh(notification)
        
        # Start new task
        await self._start_reminder_task(notification)
        
        return notification
    
    async def delete_notification(
        self,
        session: AsyncSession,
        notification_id: int
    ) -> bool:
        """Delete a notification"""
        stmt = select(TrainingNotification).where(TrainingNotification.id == notification_id)
        result = await session.execute(stmt)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        user_id = notification.user_id
        
        # Cancel tasks for this user
        await self._cancel_user_tasks(user_id)
        
        # Delete notification
        await session.delete(notification)
        await session.commit()
        
        # Restart remaining tasks
        notifications = await self.get_user_notifications(session, user_id)
        for notif in notifications:
            await self._start_reminder_task(notif)
        
        return True
    
    async def get_notification_count(self, session: AsyncSession, user_id: int) -> int:
        """Get count of active notifications for user"""
        stmt = select(TrainingNotification).where(
            TrainingNotification.user_id == user_id,
            TrainingNotification.is_active == True
        )
        result = await session.execute(stmt)
        return len(result.scalars().all())
    
    async def _start_reminder_task(self, notification: TrainingNotification):
        """Start reminder task for a notification"""
        if not self.bot:
            return
            
        # Get user telegram_id
        from src.database.connection import get_session
        async with get_session() as session:
            stmt = select(User.telegram_id).where(User.id == notification.user_id)
            result = await session.execute(stmt)
            telegram_id = result.scalar_one_or_none()
            
            if not telegram_id:
                return
        
        task = asyncio.create_task(
            self._reminder_loop(telegram_id, notification.weekday, notification.training_time)
        )
        
        if notification.user_id not in self.active_tasks:
            self.active_tasks[notification.user_id] = []
        self.active_tasks[notification.user_id].append(task)
    
    async def _reminder_loop(self, telegram_id: int, weekday: int, training_time: time):
        """Main reminder loop"""
        while True:
            try:
                now = datetime.now()
                days_ahead = weekday - now.weekday()
                if days_ahead < 0:
                    days_ahead += 7
            
                next_training = now + timedelta(days=days_ahead)
                next_training = next_training.replace(
                    hour=training_time.hour,
                    minute=training_time.minute,
                    second=0,
                    microsecond=0
                )
            
                if next_training <= now:
                    next_training += timedelta(days=7)
            
                next_reminder = next_training - timedelta(hours=1)
                if next_reminder <= now:
                    next_training += timedelta(days=7)
                    next_reminder = next_training - timedelta(hours=1)
            
                wait_seconds = (next_reminder - now).total_seconds()
                await asyncio.sleep(wait_seconds)
            
                # Get user language for reminder message
                from src.locales.translations import i18n
                from src.database.connection import get_session
                from src.services.user_service import UserService
            
                user_service = UserService()
                async with get_session() as session:
                    user = await user_service.get_user_by_telegram_id(session, telegram_id)
                    if user:
                        i18n.set_user_language(telegram_id, user.language_code)
            
                # Send localized reminder
                reminder_text = i18n.get("training_reminder", telegram_id)
                await self.bot.send_message(telegram_id, reminder_text)
            
            except asyncio.CancelledError:
                break
            except Exception:
                # Continue loop on error
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _cancel_user_tasks(self, user_id: int):
        """Cancel all tasks for a user"""
        if user_id in self.active_tasks:
            for task in self.active_tasks[user_id]:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            self.active_tasks[user_id] = []
    
    async def initialize_all_notifications(self):
        """Initialize all active notifications on bot startup"""
        from src.database.connection import get_session
        
        async with get_session() as session:
            stmt = select(TrainingNotification).where(TrainingNotification.is_active == True)
            result = await session.execute(stmt)
            notifications = result.scalars().all()
            
            for notification in notifications:
                await self._start_reminder_task(notification)
    
    def shutdown(self):
        """Shutdown all notification tasks"""
        for user_tasks in self.active_tasks.values():
            for task in user_tasks:
                task.cancel()
        self.active_tasks.clear()

# Global instance
notification_service = NotificationService()