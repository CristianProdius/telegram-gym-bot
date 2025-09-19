"""Unit tests for ExerciseService"""

import pytest

from src.services.exercise_service import ExerciseService
from src.models import Exercise

@pytest.mark.asyncio
class TestExerciseService:
    """Test exercise service functionality"""

    async def test_get_all_exercises(self, test_db, test_exercises):
        """Test getting all exercises"""
        service = ExerciseService()

        exercises = await service.get_all_exercises()

        assert len(exercises) == 5
        assert any(e.name == "Bench Press" for e in exercises)
        assert any(e.name == "Squat" for e in exercises)

    async def test_get_exercise_by_id(self, test_db, test_exercises):
        """Test getting exercise by ID"""
        service = ExerciseService()

        exercise = await service.get_exercise_by_id(test_exercises[0].id)

        assert exercise is not None
        assert exercise.name == "Bench Press"
        assert exercise.category == "Chest"

    async def test_search_exercises_exact_match(self, test_db, test_exercises):
        """Test searching exercises with exact match"""
        service = ExerciseService()

        results = await service.search_exercises("Bench Press")

        assert len(results) > 0
        assert results[0].name == "Bench Press"

    async def test_search_exercises_partial_match(self, test_db, test_exercises):
        """Test searching exercises with partial match"""
        service = ExerciseService()

        results = await service.search_exercises("press")

        assert len(results) >= 2  # Bench Press and Overhead Press
        exercise_names = [r.name for r in results]
        assert "Bench Press" in exercise_names
        assert "Overhead Press" in exercise_names

    async def test_search_exercises_by_category(self, test_db, test_exercises):
        """Test searching exercises by category"""
        service = ExerciseService()

        results = await service.search_exercises("chest")

        assert len(results) > 0
        assert any(r.category == "Chest" for r in results)

    async def test_search_exercises_by_muscle(self, test_db, test_exercises):
        """Test searching exercises by muscle group"""
        service = ExerciseService()

        results = await service.search_exercises("quadriceps")

        assert len(results) > 0
        assert any(r.muscle_group == "Quadriceps" for r in results)

    async def test_get_exercises_by_category(self, test_db, test_exercises):
        """Test getting exercises by category"""
        service = ExerciseService()

        chest_exercises = await service.get_exercises_by_category("Chest")

        assert len(chest_exercises) == 1
        assert chest_exercises[0].name == "Bench Press"

    async def test_get_exercises_by_muscle(self, test_db, test_exercises):
        """Test getting exercises by muscle group"""
        service = ExerciseService()

        back_exercises = await service.get_exercises_by_muscle("Latissimus")

        assert len(back_exercises) == 1
        assert back_exercises[0].name == "Pull-ups"

    async def test_create_custom_exercise(self, test_db, test_user):
        """Test creating a custom exercise"""
        service = ExerciseService()

        exercise = await service.create_custom_exercise(
            user_id=test_user.id,
            name="Custom Exercise",
            category="Custom",
            muscle_group="Custom Muscle",
            equipment="Custom Equipment",
            description="A custom exercise for testing"
        )

        assert exercise is not None
        assert exercise.name == "Custom Exercise"
        assert exercise.category == "Custom"
        assert exercise.description == "A custom exercise for testing"

    async def test_create_duplicate_exercise(self, test_db, test_user, test_exercises):
        """Test creating a duplicate exercise returns existing"""
        service = ExerciseService()

        exercise = await service.create_custom_exercise(
            user_id=test_user.id,
            name="Bench Press",
            category="Chest",
            muscle_group="Pectorals",
            equipment="Barbell"
        )

        assert exercise.id == test_exercises[0].id

    async def test_get_exercise_categories(self, test_db, test_exercises):
        """Test getting all exercise categories"""
        service = ExerciseService()

        categories = await service.get_exercise_categories()

        assert len(categories) == 4  # Chest, Legs, Back, Shoulders
        assert "Chest" in categories
        assert "Legs" in categories
        assert "Back" in categories
        assert "Shoulders" in categories

    async def test_get_muscle_groups(self, test_db, test_exercises):
        """Test getting all muscle groups"""
        service = ExerciseService()

        muscle_groups = await service.get_muscle_groups()

        assert len(muscle_groups) == 5
        assert "Pectorals" in muscle_groups
        assert "Quadriceps" in muscle_groups

    async def test_search_exercises_with_threshold(self, test_db, test_exercises):
        """Test search with custom threshold"""
        service = ExerciseService()

        # Low threshold should return more results
        results_low = await service.search_exercises("xyz", threshold=20)

        # High threshold should return fewer results
        results_high = await service.search_exercises("xyz", threshold=90)

        assert len(results_low) >= len(results_high)