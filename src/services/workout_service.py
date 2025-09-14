import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.models import Workout, WorkoutExercise, WorkoutSet, Exercise, User
from src.database.connection import get_session

logger = logging.getLogger(__name__)

class WorkoutService:
    """Service for managing workout data"""

    async def create_workout(
        self,
        session,
        user_id: int,
        exercise_id: int,
        sets_data: List[Dict[str, Any]],
        routine_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Workout:
        """Create a new workout with sets"""
        # Create workout
        workout = Workout(
            user_id=user_id,
            routine_id=routine_id,
            date=datetime.utcnow(),
            notes=notes
        )
        session.add(workout)
        await session.flush()

        # Create workout exercise
        workout_exercise = WorkoutExercise(
            workout_id=workout.id,
            exercise_id=exercise_id,
            order=0
        )
        session.add(workout_exercise)
        await session.flush()

        # Create sets
        for set_data in sets_data:
            workout_set = WorkoutSet(
                workout_exercise_id=workout_exercise.id,
                set_number=set_data['set_number'],
                reps=set_data['reps'],
                weight=set_data['weight'],
                rest_seconds=set_data.get('rest_seconds'),
                rpe=set_data.get('rpe'),
                notes=set_data.get('notes')
            )
            session.add(workout_set)

        await session.commit()
        logger.info(f"Created workout for user {user_id}: exercise_id={exercise_id}, sets={len(sets_data)}")
        return workout

    async def log_workout_sets(
        self,
        user_id: int,
        exercise_id: int,
        sets: List[Dict[str, Any]],
        routine_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Workout:
        """Log a new workout with multiple sets"""
        async with get_session() as session:
            # Create workout
            workout = Workout(
                user_id=user_id,
                routine_id=routine_id,
                date=datetime.now(),
                notes=notes
            )
            session.add(workout)
            await session.flush()

            # Create workout exercise
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise_id,
                order=0
            )
            session.add(workout_exercise)
            await session.flush()

            # Create sets
            for i, set_data in enumerate(sets, 1):
                workout_set = WorkoutSet(
                    workout_exercise_id=workout_exercise.id,
                    set_number=i,
                    reps=set_data.get("reps", 0),
                    weight=set_data.get("weight", 0),
                    rest_seconds=set_data.get("rest_seconds"),
                    rpe=set_data.get("rpe"),
                    notes=set_data.get("notes")
                )
                session.add(workout_set)

            await session.commit()
            logger.info(f"Logged workout for user {user_id}: exercise_id={exercise_id}, sets={len(sets)}")
            return workout

    async def get_todays_workouts(self, session, user_id: int) -> List[Workout]:
        """Get today's workouts for a user"""
        today = datetime.utcnow().date()
        stmt = (
            select(Workout)
            .where(
                Workout.user_id == user_id,
                func.date(Workout.date) == today
            )
            .options(
                selectinload(Workout.workout_exercises)
                .selectinload(WorkoutExercise.exercise),
                selectinload(Workout.workout_exercises)
                .selectinload(WorkoutExercise.sets)
            )
            .order_by(Workout.date.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().unique().all()

    async def get_today_workouts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get today's workouts for a user"""
        async with get_session() as session:
            today = datetime.now().date()
            stmt = (
                select(Workout)
                .where(
                    Workout.user_id == user_id,
                    func.date(Workout.date) == today
                )
                .options(
                    selectinload(Workout.exercises)
                    .selectinload(WorkoutExercise.exercise),
                    selectinload(Workout.exercises)
                    .selectinload(WorkoutExercise.sets)
                )
                .order_by(Workout.date.desc())
            )

            result = await session.execute(stmt)
            workouts = result.scalars().unique().all()

            workout_data = []
            for workout in workouts:
                for workout_exercise in workout.exercises:
                    exercise = workout_exercise.exercise
                    sets_data = []
                    total_volume = 0

                    for workout_set in workout_exercise.sets:
                        sets_data.append({
                            "set": workout_set.set_number,
                            "reps": workout_set.reps,
                            "weight": workout_set.weight
                        })
                        total_volume += workout_set.reps * workout_set.weight

                    workout_data.append({
                        "exercise": exercise.name,
                        "category": exercise.category,
                        "sets": sets_data,
                        "total_volume": total_volume,
                        "date": workout.date
                    })

            return workout_data

    async def get_workout_history(
        self,
        session,
        user_id: int,
        days: int = 7
    ) -> List[Workout]:
        """Get workout history for a user"""
        start_date = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(Workout)
            .where(
                Workout.user_id == user_id,
                Workout.date >= start_date
            )
            .options(
                selectinload(Workout.workout_exercises)
                .selectinload(WorkoutExercise.exercise),
                selectinload(Workout.workout_exercises)
                .selectinload(WorkoutExercise.sets)
            )
            .order_by(Workout.date.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().unique().all()

    async def get_workout_history_old(
        self,
        user_id: int,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get workout history for a user"""
        async with get_session() as session:
            start_date = datetime.now() - timedelta(days=days)
            stmt = (
                select(Workout)
                .where(
                    Workout.user_id == user_id,
                    Workout.date >= start_date
                )
                .options(
                    selectinload(Workout.exercises)
                    .selectinload(WorkoutExercise.exercise),
                    selectinload(Workout.exercises)
                    .selectinload(WorkoutExercise.sets)
                )
                .order_by(Workout.date.desc())
            )

            result = await session.execute(stmt)
            workouts = result.scalars().unique().all()

            workout_data = []
            for workout in workouts:
                for workout_exercise in workout.exercises:
                    exercise = workout_exercise.exercise
                    sets_info = []
                    for workout_set in workout_exercise.sets:
                        sets_info.append(f"{workout_set.reps}x{workout_set.weight}kg")

                    workout_data.append({
                        "exercise": exercise.name,
                        "sets_info": ", ".join(sets_info),
                        "date": workout.date
                    })

            return workout_data

    async def get_exercise_stats(
        self,
        user_id: int,
        exercise_id: int
    ) -> Dict[str, Any]:
        """Get statistics for a specific exercise"""
        async with get_session() as session:
            # Get all workout sets for this exercise
            stmt = (
                select(WorkoutSet)
                .join(WorkoutExercise)
                .join(Workout)
                .where(
                    Workout.user_id == user_id,
                    WorkoutExercise.exercise_id == exercise_id
                )
            )

            result = await session.execute(stmt)
            sets = result.scalars().all()

            if not sets:
                return {
                    "exercise_id": exercise_id,
                    "total_workouts": 0,
                    "total_sets": 0,
                    "total_reps": 0,
                    "total_volume": 0,
                    "max_weight": 0,
                    "avg_weight": 0,
                    "max_reps": 0
                }

            # Calculate statistics
            total_sets = len(sets)
            total_reps = sum(s.reps for s in sets)
            total_volume = sum(s.reps * s.weight for s in sets)
            max_weight = max(s.weight for s in sets)
            avg_weight = sum(s.weight for s in sets) / len(sets)
            max_reps = max(s.reps for s in sets)

            # Count unique workout sessions
            workout_ids = set()
            for s in sets:
                stmt = select(WorkoutExercise.workout_id).where(
                    WorkoutExercise.id == s.workout_exercise_id
                )
                result = await session.execute(stmt)
                workout_id = result.scalar()
                if workout_id:
                    workout_ids.add(workout_id)

            return {
                "exercise_id": exercise_id,
                "total_workouts": len(workout_ids),
                "total_sets": total_sets,
                "total_reps": total_reps,
                "total_volume": round(total_volume, 2),
                "max_weight": max_weight,
                "avg_weight": round(avg_weight, 2),
                "max_reps": max_reps
            }

    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get overall statistics for a user"""
        async with get_session() as session:
            # Total workouts
            stmt = select(func.count(Workout.id)).where(Workout.user_id == user_id)
            result = await session.execute(stmt)
            total_workouts = result.scalar() or 0

            # This week's workouts
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            stmt = select(func.count(Workout.id)).where(
                Workout.user_id == user_id,
                Workout.date >= week_start
            )
            result = await session.execute(stmt)
            week_workouts = result.scalar() or 0

            # Total volume
            stmt = (
                select(func.sum(WorkoutSet.reps * WorkoutSet.weight))
                .join(WorkoutExercise)
                .join(Workout)
                .where(Workout.user_id == user_id)
            )
            result = await session.execute(stmt)
            total_volume = result.scalar() or 0

            # Favorite exercise
            stmt = (
                select(
                    Exercise.name,
                    func.count(WorkoutExercise.id).label("count")
                )
                .join(WorkoutExercise)
                .join(Workout)
                .where(Workout.user_id == user_id)
                .group_by(Exercise.id)
                .order_by(func.count(WorkoutExercise.id).desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            favorite = result.first()
            favorite_exercise = favorite[0] if favorite else "None"

            return {
                "total_workouts": total_workouts,
                "week_workouts": week_workouts,
                "total_volume": round(total_volume, 2),
                "favorite_exercise": favorite_exercise
            }

    async def calculate_one_rep_max(
        self,
        user_id: int,
        exercise_id: int
    ) -> float:
        """Calculate estimated one-rep max using Brzycki formula"""
        stats = await self.get_exercise_stats(user_id, exercise_id)

        if stats["max_weight"] == 0:
            return 0

        # Brzycki formula: 1RM = weight * (36 / (37 - reps))
        # Using the max weight with its corresponding reps
        async with get_session() as session:
            stmt = (
                select(WorkoutSet)
                .join(WorkoutExercise)
                .join(Workout)
                .where(
                    Workout.user_id == user_id,
                    WorkoutExercise.exercise_id == exercise_id,
                    WorkoutSet.weight == stats["max_weight"]
                )
                .order_by(WorkoutSet.reps.asc())
                .limit(1)
            )
            result = await session.execute(stmt)
            max_set = result.scalar_one_or_none()

            if not max_set or max_set.reps >= 37:
                return stats["max_weight"]

            one_rm = max_set.weight * (36 / (37 - max_set.reps))
            return round(one_rm, 2)