import logging
from typing import List, Optional, Dict, Any
from fuzzywuzzy import fuzz
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.models import Exercise
from src.database.connection import get_session

logger = logging.getLogger(__name__)

class ExerciseService:
    """Service for managing exercises"""

    async def get_all_exercises(self, session) -> List[Exercise]:
        """Get all exercises from database"""
        stmt = select(Exercise).order_by(Exercise.category, Exercise.name)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_exercise_by_id(self, session, exercise_id: int) -> Optional[Exercise]:
        """Get exercise by ID"""
        stmt = select(Exercise).where(Exercise.id == exercise_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_exercises(
        self,
        session,
        query: str,
        limit: int = 10,
        threshold: int = 60
    ) -> List[Exercise]:
        """Search exercises with fuzzy matching"""
        all_exercises = await self.get_all_exercises(session)
        scored_exercises = []

        for exercise in all_exercises:
            # Calculate similarity score
            name_score = fuzz.partial_ratio(query.lower(), exercise.name.lower())
            category_score = fuzz.partial_ratio(query.lower(), exercise.category.lower())
            muscle_score = fuzz.partial_ratio(query.lower(), exercise.muscle_group.lower())

            # Take the highest score
            max_score = max(name_score, category_score * 0.7, muscle_score * 0.7)

            if max_score >= threshold:
                scored_exercises.append((exercise, max_score))

        # Sort by score and return top results
        scored_exercises.sort(key=lambda x: x[1], reverse=True)
        return [ex[0] for ex in scored_exercises[:limit]]

    async def get_exercises_by_category(self, session, category: str) -> List[Exercise]:
        """Get exercises by category"""
        stmt = select(Exercise).where(
            Exercise.category == category
        ).order_by(Exercise.name)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_exercises_by_muscle(self, muscle_group: str) -> List[Exercise]:
        """Get exercises by muscle group"""
        async with get_session() as session:
            stmt = select(Exercise).where(
                Exercise.muscle_group.contains(muscle_group)
            ).order_by(Exercise.name)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_popular_exercises(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently used exercises by user"""
        async with get_session() as session:
            from src.models import WorkoutExercise, Workout

            stmt = (
                select(
                    Exercise,
                    func.count(WorkoutExercise.id).label("usage_count")
                )
                .join(WorkoutExercise, Exercise.id == WorkoutExercise.exercise_id)
                .join(Workout, WorkoutExercise.workout_id == Workout.id)
                .where(Workout.user_id == user_id)
                .group_by(Exercise.id)
                .order_by(func.count(WorkoutExercise.id).desc())
                .limit(limit)
            )

            result = await session.execute(stmt)
            exercises = []

            for row in result:
                exercise, count = row
                exercises.append({
                    "exercise": exercise,
                    "usage_count": count
                })

            return exercises

    async def create_custom_exercise(
        self,
        user_id: int,
        name: str,
        category: str,
        muscle_group: str,
        equipment: Optional[str] = None,
        description: Optional[str] = None
    ) -> Exercise:
        """Create a custom exercise for user"""
        async with get_session() as session:
            # Check if exercise already exists
            stmt = select(Exercise).where(Exercise.name == name)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return existing

            # Create new exercise
            exercise = Exercise(
                name=name,
                category=category,
                muscle_group=muscle_group,
                equipment=equipment,
                description=description
            )

            session.add(exercise)
            await session.commit()
            await session.refresh(exercise)

            logger.info(f"Created custom exercise '{name}' for user {user_id}")
            return exercise

    async def get_exercise_categories(self) -> List[str]:
        """Get all unique exercise categories"""
        async with get_session() as session:
            stmt = select(Exercise.category).distinct().order_by(Exercise.category)
            result = await session.execute(stmt)
            return [cat for cat in result.scalars() if cat]

    async def get_muscle_groups(self) -> List[str]:
        """Get all unique muscle groups"""
        async with get_session() as session:
            stmt = select(Exercise.muscle_group).distinct().order_by(Exercise.muscle_group)
            result = await session.execute(stmt)
            return [muscle for muscle in result.scalars() if muscle]