import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models import Routine, RoutineExercise, Exercise, User
from src.database.connection import get_session

logger = logging.getLogger(__name__)

class RoutineService:
    """Service for managing workout routines"""

    async def create_routine(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: str = "intermediate",
        is_public: bool = False
    ) -> Routine:
        """Create a new workout routine"""
        async with get_session() as session:
            routine = Routine(
                user_id=user_id,
                name=name,
                description=description,
                category=category,
                difficulty=difficulty,
                is_public=is_public
            )
            session.add(routine)
            await session.commit()
            await session.refresh(routine)

            logger.info(f"Created routine '{name}' for user {user_id}")
            return routine

    async def add_exercise_to_routine(
        self,
        routine_id: int,
        exercise_id: int,
        day: Optional[int] = None,
        order: int = 0,
        target_sets: Optional[int] = None,
        target_reps_min: Optional[int] = None,
        target_reps_max: Optional[int] = None,
        target_weight: Optional[float] = None,
        rest_seconds: int = 90,
        notes: Optional[str] = None
    ) -> RoutineExercise:
        """Add an exercise to a routine"""
        async with get_session() as session:
            routine_exercise = RoutineExercise(
                routine_id=routine_id,
                exercise_id=exercise_id,
                day=day,
                order=order,
                target_sets=target_sets,
                target_reps_min=target_reps_min,
                target_reps_max=target_reps_max,
                target_weight=target_weight,
                rest_seconds=rest_seconds,
                notes=notes
            )
            session.add(routine_exercise)
            await session.commit()
            await session.refresh(routine_exercise)

            return routine_exercise

    async def get_user_routines(self, user_id: int) -> List[Routine]:
        """Get all routines for a user"""
        async with get_session() as session:
            stmt = (
                select(Routine)
                .where(Routine.user_id == user_id)
                .options(
                    selectinload(Routine.routine_exercises)
                    .selectinload(RoutineExercise.exercise)
                )
                .order_by(Routine.created_at.desc())
            )

            result = await session.execute(stmt)
            return result.scalars().unique().all()

    async def get_public_routines(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[Routine]:
        """Get public routines with optional filters"""
        async with get_session() as session:
            stmt = select(Routine).where(Routine.is_public == True)

            if category:
                stmt = stmt.where(Routine.category == category)
            if difficulty:
                stmt = stmt.where(Routine.difficulty == difficulty)

            stmt = stmt.options(
                selectinload(Routine.routine_exercises)
                .selectinload(RoutineExercise.exercise)
            ).order_by(Routine.created_at.desc())

            result = await session.execute(stmt)
            return result.scalars().unique().all()

    async def get_routine_details(self, routine_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a routine"""
        async with get_session() as session:
            stmt = (
                select(Routine)
                .where(Routine.id == routine_id)
                .options(
                    selectinload(Routine.routine_exercises)
                    .selectinload(RoutineExercise.exercise)
                )
            )

            result = await session.execute(stmt)
            routine = result.scalar_one_or_none()

            if not routine:
                return None

            exercises_by_day = {}
            for routine_exercise in routine.routine_exercises:
                day = routine_exercise.day or 1
                if day not in exercises_by_day:
                    exercises_by_day[day] = []

                exercises_by_day[day].append({
                    "exercise": routine_exercise.exercise.name,
                    "category": routine_exercise.exercise.category,
                    "muscle_group": routine_exercise.exercise.muscle_group,
                    "target_sets": routine_exercise.target_sets,
                    "target_reps": f"{routine_exercise.target_reps_min}-{routine_exercise.target_reps_max}"
                    if routine_exercise.target_reps_min and routine_exercise.target_reps_max
                    else None,
                    "target_weight": routine_exercise.target_weight,
                    "rest_seconds": routine_exercise.rest_seconds,
                    "notes": routine_exercise.notes
                })

            return {
                "id": routine.id,
                "name": routine.name,
                "description": routine.description,
                "category": routine.category,
                "difficulty": routine.difficulty,
                "is_public": routine.is_public,
                "exercises_by_day": exercises_by_day,
                "total_exercises": len(routine.routine_exercises),
                "created_at": routine.created_at
            }

    async def duplicate_routine(
        self,
        user_id: int,
        routine_id: int,
        new_name: Optional[str] = None
    ) -> Routine:
        """Duplicate an existing routine for a user"""
        async with get_session() as session:
            # Get original routine
            stmt = (
                select(Routine)
                .where(Routine.id == routine_id)
                .options(selectinload(Routine.routine_exercises))
            )
            result = await session.execute(stmt)
            original = result.scalar_one_or_none()

            if not original:
                raise ValueError("Routine not found")

            # Create new routine
            new_routine = Routine(
                user_id=user_id,
                name=new_name or f"{original.name} (Copy)",
                description=original.description,
                category=original.category,
                difficulty=original.difficulty,
                is_public=False
            )
            session.add(new_routine)
            await session.flush()

            # Copy exercises
            for orig_exercise in original.routine_exercises:
                new_exercise = RoutineExercise(
                    routine_id=new_routine.id,
                    exercise_id=orig_exercise.exercise_id,
                    day=orig_exercise.day,
                    order=orig_exercise.order,
                    target_sets=orig_exercise.target_sets,
                    target_reps_min=orig_exercise.target_reps_min,
                    target_reps_max=orig_exercise.target_reps_max,
                    target_weight=orig_exercise.target_weight,
                    rest_seconds=orig_exercise.rest_seconds,
                    notes=orig_exercise.notes
                )
                session.add(new_exercise)

            await session.commit()
            await session.refresh(new_routine)

            logger.info(f"Duplicated routine {routine_id} for user {user_id}")
            return new_routine

    async def delete_routine(self, user_id: int, routine_id: int) -> bool:
        """Delete a routine"""
        async with get_session() as session:
            stmt = select(Routine).where(
                Routine.id == routine_id,
                Routine.user_id == user_id
            )
            result = await session.execute(stmt)
            routine = result.scalar_one_or_none()

            if routine:
                await session.delete(routine)
                await session.commit()
                logger.info(f"Deleted routine {routine_id} for user {user_id}")
                return True

            return False

    async def get_popular_routines(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular public routines"""
        async with get_session() as session:
            from src.models import Workout
            from sqlalchemy import func

            stmt = (
                select(
                    Routine,
                    func.count(Workout.id).label("usage_count")
                )
                .outerjoin(Workout, Routine.id == Workout.routine_id)
                .where(Routine.is_public == True)
                .group_by(Routine.id)
                .order_by(func.count(Workout.id).desc())
                .limit(limit)
            )

            result = await session.execute(stmt)
            routines = []

            for row in result:
                routine, count = row
                routines.append({
                    "routine": routine,
                    "usage_count": count
                })

            return routines

    async def create_preset_routines(self):
        """Create preset workout routines"""
        preset_routines = [
            {
                "name": "Push Pull Legs (PPL)",
                "description": "Classic 3-day split focusing on push, pull, and leg movements",
                "category": "PPL",
                "difficulty": "intermediate",
                "is_public": True,
                "days": {
                    1: [  # Push Day
                        {"exercise": "Bench Press", "sets": 4, "reps_min": 6, "reps_max": 8},
                        {"exercise": "Overhead Press", "sets": 3, "reps_min": 8, "reps_max": 10},
                        {"exercise": "Dips", "sets": 3, "reps_min": 8, "reps_max": 12},
                        {"exercise": "Lateral Raises", "sets": 3, "reps_min": 12, "reps_max": 15},
                        {"exercise": "Tricep Pushdown", "sets": 3, "reps_min": 12, "reps_max": 15}
                    ],
                    2: [  # Pull Day
                        {"exercise": "Deadlift", "sets": 4, "reps_min": 5, "reps_max": 6},
                        {"exercise": "Pull-ups", "sets": 3, "reps_min": 6, "reps_max": 10},
                        {"exercise": "Barbell Row", "sets": 3, "reps_min": 8, "reps_max": 10},
                        {"exercise": "Face Pulls", "sets": 3, "reps_min": 12, "reps_max": 15},
                        {"exercise": "Barbell Curl", "sets": 3, "reps_min": 10, "reps_max": 12}
                    ],
                    3: [  # Leg Day
                        {"exercise": "Squat", "sets": 4, "reps_min": 6, "reps_max": 8},
                        {"exercise": "Romanian Deadlift", "sets": 3, "reps_min": 8, "reps_max": 10},
                        {"exercise": "Leg Press", "sets": 3, "reps_min": 10, "reps_max": 12},
                        {"exercise": "Leg Curl", "sets": 3, "reps_min": 12, "reps_max": 15},
                        {"exercise": "Calf Raises", "sets": 4, "reps_min": 12, "reps_max": 15}
                    ]
                }
            },
            {
                "name": "StrongLifts 5x5",
                "description": "Simple but effective strength program with 5 sets of 5 reps",
                "category": "Strength",
                "difficulty": "beginner",
                "is_public": True,
                "days": {
                    1: [  # Workout A
                        {"exercise": "Squat", "sets": 5, "reps_min": 5, "reps_max": 5},
                        {"exercise": "Bench Press", "sets": 5, "reps_min": 5, "reps_max": 5},
                        {"exercise": "Barbell Row", "sets": 5, "reps_min": 5, "reps_max": 5}
                    ],
                    2: [  # Workout B
                        {"exercise": "Squat", "sets": 5, "reps_min": 5, "reps_max": 5},
                        {"exercise": "Overhead Press", "sets": 5, "reps_min": 5, "reps_max": 5},
                        {"exercise": "Deadlift", "sets": 1, "reps_min": 5, "reps_max": 5}
                    ]
                }
            },
            {
                "name": "Upper/Lower Split",
                "description": "4-day split alternating between upper and lower body",
                "category": "Upper/Lower",
                "difficulty": "intermediate",
                "is_public": True,
                "days": {
                    1: [  # Upper A
                        {"exercise": "Bench Press", "sets": 4, "reps_min": 6, "reps_max": 8},
                        {"exercise": "Barbell Row", "sets": 4, "reps_min": 6, "reps_max": 8},
                        {"exercise": "Overhead Press", "sets": 3, "reps_min": 8, "reps_max": 10},
                        {"exercise": "Pull-ups", "sets": 3, "reps_min": 8, "reps_max": 10},
                        {"exercise": "Dumbbell Curl", "sets": 3, "reps_min": 10, "reps_max": 12}
                    ],
                    2: [  # Lower A
                        {"exercise": "Squat", "sets": 4, "reps_min": 6, "reps_max": 8},
                        {"exercise": "Romanian Deadlift", "sets": 3, "reps_min": 8, "reps_max": 10},
                        {"exercise": "Leg Press", "sets": 3, "reps_min": 10, "reps_max": 12},
                        {"exercise": "Leg Curl", "sets": 3, "reps_min": 10, "reps_max": 12},
                        {"exercise": "Calf Raises", "sets": 4, "reps_min": 12, "reps_max": 15}
                    ]
                }
            }
        ]

        # Create system user for preset routines
        system_user_id = 0

        for routine_data in preset_routines:
            # Check if routine already exists
            async with get_session() as session:
                stmt = select(Routine).where(
                    Routine.name == routine_data["name"],
                    Routine.user_id == system_user_id
                )
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    continue

                # Create routine
                routine = await self.create_routine(
                    user_id=system_user_id,
                    name=routine_data["name"],
                    description=routine_data["description"],
                    category=routine_data["category"],
                    difficulty=routine_data["difficulty"],
                    is_public=routine_data["is_public"]
                )

                # Add exercises
                from src.services.exercise_service import ExerciseService
                exercise_service = ExerciseService()

                for day, exercises in routine_data["days"].items():
                    for order, exercise_data in enumerate(exercises):
                        # Find exercise
                        exercises_list = await exercise_service.search_exercises(
                            exercise_data["exercise"],
                            limit=1
                        )

                        if exercises_list:
                            await self.add_exercise_to_routine(
                                routine_id=routine.id,
                                exercise_id=exercises_list[0].id,
                                day=day,
                                order=order,
                                target_sets=exercise_data["sets"],
                                target_reps_min=exercise_data["reps_min"],
                                target_reps_max=exercise_data["reps_max"],
                                rest_seconds=90 if "Squat" in exercise_data["exercise"] or "Deadlift" in exercise_data["exercise"] else 60
                            )

                logger.info(f"Created preset routine: {routine_data['name']}")