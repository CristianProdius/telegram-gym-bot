"""User service for managing user data"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User

class UserService:
    """Service for user-related operations"""

    async def get_user(self, session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID"""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
  
    async def get_or_create_user(
        self,
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "en"
    ) -> User:
        """Get existing user or create a new one"""
        # Try to get existing user
        user = await self.get_user(session, telegram_id)

        if user:
            # Update last active time
            user.last_active = datetime.utcnow()
            # Update username if changed
            if username and user.username != username:
                user.username = username
            await session.commit()
            await session.refresh(user)
            return user

        # Create new user
        return await self.create_user(
            session,
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code
        )

    async def create_user(
        self,
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "en"
    ) -> User:
        """Create a new user"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            is_active=True,
            weight_unit="kg",
            timezone="UTC",
            notification_enabled=False
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def update_user_language(self, session: AsyncSession, telegram_id: int, language_code: str):
        """Update user's language preference"""
        user = await self.get_user(session, telegram_id)
        if user:
            user.language_code = language_code
            await session.commit()
    
    async def update_last_active(self, session: AsyncSession, telegram_id: int):
        """Update user's last active timestamp"""
        user = await self.get_user(session, telegram_id)
        if user:
            user.last_active = datetime.utcnow()
            await session.commit()

    async def get_user_stats(self, session: AsyncSession, telegram_id: int) -> dict:
        """Get user statistics"""
        from src.models.workout import Workout
        from sqlalchemy import func

        user = await self.get_user(session, telegram_id)
        if not user:
            return {}

        # Get workout statistics
        stmt = select(func.count(Workout.id)).where(Workout.user_id == user.id)
        result = await session.execute(stmt)
        total_workouts = result.scalar() or 0

        # Get this week's workouts
        week_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = week_start - timedelta(days=week_start.weekday())

        stmt = select(func.count(Workout.id)).where(
            Workout.user_id == user.id,
            Workout.date >= week_start
        )
        result = await session.execute(stmt)
        week_workouts = result.scalar() or 0

        return {
            "total_workouts": total_workouts,
            "week_workouts": week_workouts,
            "member_since": user.created_at.strftime("%B %Y"),
            "last_active": user.last_active.strftime("%Y-%m-%d %H:%M")
        }
    
    async def get_user_by_telegram_id(self, session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID (alias for get_user for clarity)"""
        return await self.get_user(session, telegram_id)
