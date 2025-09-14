"""Unit tests for WorkoutService"""

import pytest
from datetime import datetime, timedelta

from src.services.workout_service import WorkoutService
from src.models import User, Exercise

@pytest.mark.asyncio
class TestWorkoutService:
    """Test workout service functionality"""

    async def test_log_workout_sets(self, test_db, test_user, test_exercises):
        """Test logging a workout with multiple sets"""
        service = WorkoutService()

        sets_data = [
            {"reps": 10, "weight": 60.0},
            {"reps": 8, "weight": 65.0},
            {"reps": 6, "weight": 70.0}
        ]

        workout = await service.log_workout_sets(
            user_id=test_user.id,
            exercise_id=test_exercises[0].id,
            sets=sets_data,
            notes="Test workout"
        )

        assert workout is not None
        assert workout.user_id == test_user.id
        assert workout.notes == "Test workout"

    async def test_get_today_workouts(self, test_db, test_user, test_workout):
        """Test getting today's workouts"""
        service = WorkoutService()

        workouts = await service.get_today_workouts(test_user.id)

        assert len(workouts) > 0
        assert workouts[0]["exercise"] == "Bench Press"
        assert len(workouts[0]["sets"]) == 3

    async def test_get_workout_history(self, test_db, test_user, test_workout):
        """Test getting workout history"""
        service = WorkoutService()

        history = await service.get_workout_history(test_user.id, days=7)

        assert len(history) > 0
        assert history[0]["exercise"] == "Bench Press"
        assert "60.0kg" in history[0]["sets_info"]

    async def test_get_exercise_stats(self, test_db, test_user, test_workout, test_exercises):
        """Test getting exercise statistics"""
        service = WorkoutService()

        stats = await service.get_exercise_stats(
            user_id=test_user.id,
            exercise_id=test_exercises[0].id
        )

        assert stats["total_workouts"] == 1
        assert stats["total_sets"] == 3
        assert stats["total_reps"] == 30  # 10 + 10 + 10
        assert stats["max_weight"] == 65.0
        assert stats["max_reps"] == 10

    async def test_get_user_statistics(self, test_db, test_user, test_workout):
        """Test getting overall user statistics"""
        service = WorkoutService()

        stats = await service.get_user_statistics(test_user.id)

        assert stats["total_workouts"] == 1
        assert stats["total_volume"] > 0
        assert stats["favorite_exercise"] == "Bench Press"

    async def test_calculate_one_rep_max(self, test_db, test_user, test_workout, test_exercises):
        """Test one-rep max calculation"""
        service = WorkoutService()

        one_rm = await service.calculate_one_rep_max(
            user_id=test_user.id,
            exercise_id=test_exercises[0].id
        )

        # Brzycki formula: 65kg * (36 / (37 - 10)) ≈ 86.67kg
        assert one_rm > 80
        assert one_rm < 90

    async def test_empty_workout_history(self, test_db, test_user):
        """Test getting workout history for user with no workouts"""
        service = WorkoutService()

        history = await service.get_workout_history(test_user.id)

        assert history == []

    async def test_exercise_stats_no_data(self, test_db, test_user, test_exercises):
        """Test exercise stats when no data exists"""
        service = WorkoutService()

        stats = await service.get_exercise_stats(
            user_id=test_user.id,
            exercise_id=test_exercises[1].id  # Squat - no data
        )

        assert stats["total_workouts"] == 0
        assert stats["total_sets"] == 0
        assert stats["total_reps"] == 0
        assert stats["max_weight"] == 0