"""Unit tests for Analytics Service"""

import pytest
from datetime import datetime, timedelta

from src.services.analytics_service import WorkoutAnalytics
from src.services.workout_service import WorkoutService

@pytest.mark.asyncio
class TestWorkoutAnalytics:
    """Test workout analytics functionality"""

    async def test_calculate_volume_progression(self, test_db, test_user, test_workout):
        """Test volume progression calculation"""
        analytics = WorkoutAnalytics()

        result = await analytics.calculate_volume_progression(test_user.id, weeks=12)

        assert "weekly_volumes" in result
        assert "trend" in result
        assert "average_increase" in result
        assert "projection" in result

    async def test_identify_weak_points(self, test_db, test_user, test_workout):
        """Test identifying weak muscle groups"""
        analytics = WorkoutAnalytics()

        result = await analytics.identify_weak_points(test_user.id)

        assert "muscle_distribution" in result
        assert "weak_points" in result
        assert "total_volume" in result
        assert result["total_volume"] > 0

    async def test_generate_recommendations(self, test_db, test_user, test_workout):
        """Test generating workout recommendations"""
        analytics = WorkoutAnalytics()

        recommendations = await analytics.generate_recommendations(test_user.id)

        assert isinstance(recommendations, list)
        # Should have at least frequency recommendation
        assert len(recommendations) > 0
        assert all("type" in r for r in recommendations)
        assert all("priority" in r for r in recommendations)
        assert all("message" in r for r in recommendations)
        assert all("suggestion" in r for r in recommendations)

    async def test_get_personal_records_empty(self, test_db, test_user):
        """Test getting personal records when none exist"""
        analytics = WorkoutAnalytics()

        records = await analytics.get_personal_records(test_user.id)

        assert records == []

    async def test_check_and_update_personal_records(self, test_db, test_user, test_workout):
        """Test checking and updating personal records"""
        analytics = WorkoutAnalytics()

        new_records = await analytics.check_and_update_personal_records(
            test_user.id,
            test_workout.id
        )

        assert isinstance(new_records, list)
        # Should have found at least one record from the test workout
        assert len(new_records) >= 1
        assert all("exercise" in r for r in new_records)
        assert all("type" in r for r in new_records)
        assert all("value" in r for r in new_records)

    async def test_volume_progression_no_data(self, test_db, test_user):
        """Test volume progression with no workout data"""
        analytics = WorkoutAnalytics()

        result = await analytics.calculate_volume_progression(test_user.id, weeks=12)

        assert result["weekly_volumes"] == {}
        assert result["trend"] == 0
        assert result["average_increase"] == 0
        assert result["projection"] == {}

    async def test_weak_points_no_data(self, test_db, test_user):
        """Test weak points identification with no data"""
        analytics = WorkoutAnalytics()

        result = await analytics.identify_weak_points(test_user.id)

        assert result["weak_points"] == []
        assert result["total_volume"] == 0

    async def test_recommendations_frequency(self, test_db, test_user):
        """Test frequency recommendations"""
        analytics = WorkoutAnalytics()

        # User with no workouts should get frequency recommendation
        recommendations = await analytics.generate_recommendations(test_user.id)

        frequency_recs = [r for r in recommendations if r["type"] == "frequency"]
        assert len(frequency_recs) > 0
        assert frequency_recs[0]["priority"] == "high"

    async def test_multiple_muscle_groups(self, test_db, test_user, test_exercises):
        """Test analytics with multiple muscle groups"""
        service = WorkoutService()
        analytics = WorkoutAnalytics()

        # Log workouts for different muscle groups
        for exercise in test_exercises[:3]:
            await service.log_workout_sets(
                user_id=test_user.id,
                exercise_id=exercise.id,
                sets=[{"reps": 10, "weight": 50.0}]
            )

        result = await analytics.identify_weak_points(test_user.id)

        assert len(result["muscle_distribution"]) >= 3
        assert result["total_volume"] > 0