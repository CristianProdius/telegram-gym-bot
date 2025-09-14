"""Statistics and profile handlers"""

import logging
from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from src.services.user_service import UserService
from src.services.workout_service import WorkoutService
from src.services.analytics_service import WorkoutAnalytics as AnalyticsService
from src.locales.translations import i18n
from src.database.connection import get_session

logger = logging.getLogger(__name__)

def register_stats_handlers(dp: Dispatcher):
    """Register statistics and profile handlers"""
    router = Router()

    @router.message(Command("stats"))
    async def cmd_stats(message: Message):
        """Show user statistics"""
        user_id = message.from_user.id
        logger.info(f"User {user_id} requested stats")

        async with get_session() as session:
            user_service = UserService()
            user = await user_service.get_user(session, user_id)

            if not user:
                await message.answer(i18n.get("error_not_found", user_id))
                return

            # Get user stats
            stats = await user_service.get_user_stats(session, user_id)

            # Format stats message
            stats_text = i18n.get(
                "stats_overview",
                user_id,
                total_workouts=stats.get("total_workouts", 0),
                week_workouts=stats.get("week_workouts", 0),
                total_volume=stats.get("total_volume", 0),
                favorite=stats.get("favorite_exercise", "N/A")
            )

            await message.answer(stats_text)

    @router.message(Command("profile"))
    async def cmd_profile(message: Message):
        """Show user profile"""
        user_id = message.from_user.id
        logger.info(f"User {user_id} requested profile")

        async with get_session() as session:
            user_service = UserService()
            user = await user_service.get_user(session, user_id)

            if not user:
                await message.answer(i18n.get("error_not_found", user_id))
                return

            profile_text = f"""
👤 <b>Profile</b>

Name: {user.first_name or 'Not set'} {user.last_name or ''}
Username: @{user.username or 'Not set'}
Member since: {user.created_at.strftime('%B %Y')}
Language: {'🇬🇧 English' if user.language_code == 'en' else '🇷🇺 Русский'}
Weight unit: {user.weight_unit}
Timezone: {user.timezone}

Use /settings to change preferences
"""
            await message.answer(profile_text)

    @router.message(Command("today"))
    async def cmd_today(message: Message):
        """Show today's workouts"""
        user_id = message.from_user.id
        logger.info(f"User {user_id} requested today's workouts")

        async with get_session() as session:
            user_service = UserService()
            workout_service = WorkoutService()

            user = await user_service.get_user(session, user_id)
            if not user:
                await message.answer(i18n.get("error_not_found", user_id))
                return

            # Get today's workouts
            workouts = await workout_service.get_todays_workouts(session, user.id)

            if not workouts:
                await message.answer(i18n.get("no_workouts_today", user_id))
                return

            # Format workout list
            text = "📅 <b>Today's Workouts</b>\n\n"
            for workout in workouts:
                text += f"🏋️ {workout.date.strftime('%H:%M')}\n"
                for we in workout.workout_exercises:
                    text += f"  • {we.exercise.name}: "
                    sets_info = [f"{s.reps}x{s.weight}kg" for s in we.sets]
                    text += ", ".join(sets_info) + "\n"
                text += "\n"

            await message.answer(text)

    @router.message(Command("history"))
    async def cmd_history(message: Message):
        """Show workout history"""
        user_id = message.from_user.id
        logger.info(f"User {user_id} requested workout history")

        async with get_session() as session:
            user_service = UserService()
            workout_service = WorkoutService()

            user = await user_service.get_user(session, user_id)
            if not user:
                await message.answer(i18n.get("error_not_found", user_id))
                return

            # Get last 7 days of workouts
            workouts = await workout_service.get_workout_history(session, user.id, days=7)

            if not workouts:
                await message.answer("No workouts in the last 7 days")
                return

            # Format history
            text = i18n.get("workout_history", user_id, days=7) + "\n\n"
            current_date = None

            for workout in workouts:
                workout_date = workout.date.strftime('%Y-%m-%d')
                if workout_date != current_date:
                    current_date = workout_date
                    text += f"\n📅 <b>{workout_date}</b>\n"

                for we in workout.workout_exercises:
                    text += f"  • {we.exercise.name}: "
                    total_volume = sum(s.reps * s.weight for s in we.sets)
                    text += f"{len(we.sets)} sets, {total_volume:.0f}kg volume\n"

            await message.answer(text)

    @router.message(Command("records", "pr"))
    async def cmd_records(message: Message):
        """Show personal records"""
        user_id = message.from_user.id
        logger.info(f"User {user_id} requested personal records")

        async with get_session() as session:
            user_service = UserService()
            analytics_service = AnalyticsService()

            user = await user_service.get_user(session, user_id)
            if not user:
                await message.answer(i18n.get("error_not_found", user_id))
                return

            # Get personal records
            records = await analytics_service.get_personal_records(session, user.id)

            if not records:
                await message.answer(i18n.get("no_records", user_id))
                return

            # Format records
            records_text = "🏆 <b>Personal Records</b>\n\n"
            for record in records[:10]:  # Show top 10
                records_text += f"💪 {record.exercise.name}\n"
                records_text += f"   {record.record_type}: {record.value:.1f}"
                if record.record_type in ["max_weight", "total_volume"]:
                    records_text += "kg"
                records_text += f"\n   📅 {record.date_achieved.strftime('%Y-%m-%d')}\n\n"

            await message.answer(records_text)

    dp.include_router(router)