import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import numpy as np
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.models import Workout, WorkoutExercise, WorkoutSet, Exercise, ProgressRecord, PersonalRecord
from src.database.connection import get_session

logger = logging.getLogger(__name__)

class WorkoutAnalytics:
    """Comprehensive workout analytics system"""

    async def calculate_volume_progression(
        self,
        user_id: int,
        weeks: int = 12
    ) -> Dict[str, Any]:
        """Calculate weekly volume progression with trend analysis"""
        async with get_session() as session:
            start_date = datetime.now() - timedelta(weeks=weeks * 7)

            stmt = (
                select(Workout)
                .where(
                    Workout.user_id == user_id,
                    Workout.date >= start_date
                )
                .options(
                    selectinload(Workout.exercises)
                    .selectinload(WorkoutExercise.sets)
                )
                .order_by(Workout.date)
            )

            result = await session.execute(stmt)
            workouts = result.scalars().unique().all()

            weekly_volumes = defaultdict(float)

            for workout in workouts:
                week = workout.date.isocalendar()[1]
                year = workout.date.isocalendar()[0]
                week_key = f"{year}-W{week:02d}"

                for workout_exercise in workout.exercises:
                    for workout_set in workout_exercise.sets:
                        volume = workout_set.weight * workout_set.reps
                        weekly_volumes[week_key] += volume

            # Calculate trend if we have data
            if len(weekly_volumes) > 1:
                volumes = list(weekly_volumes.values())
                x = np.arange(len(volumes))
                trend = np.polyfit(x, volumes, 1)[0]

                return {
                    "weekly_volumes": dict(weekly_volumes),
                    "trend": trend,
                    "average_increase": trend * 7,
                    "projection": self._project_future_volume(weekly_volumes, trend)
                }

            return {
                "weekly_volumes": dict(weekly_volumes),
                "trend": 0,
                "average_increase": 0,
                "projection": {}
            }

    def _project_future_volume(
        self,
        weekly_volumes: Dict[str, float],
        trend: float,
        weeks_ahead: int = 4
    ) -> Dict[str, float]:
        """Project future volume based on trend"""
        if not weekly_volumes:
            return {}

        last_volume = list(weekly_volumes.values())[-1]
        projection = {}

        for i in range(1, weeks_ahead + 1):
            projected_volume = last_volume + (trend * i * 7)
            week_date = datetime.now() + timedelta(weeks=i)
            week_key = f"{week_date.year}-W{week_date.isocalendar()[1]:02d}"
            projection[week_key] = max(0, projected_volume)

        return projection

    async def identify_weak_points(self, user_id: int) -> Dict[str, Any]:
        """Identify lagging muscle groups based on volume distribution"""
        async with get_session() as session:
            # Get muscle group volumes
            stmt = (
                select(
                    Exercise.muscle_group,
                    func.sum(WorkoutSet.reps * WorkoutSet.weight).label("total_volume"),
                    func.count(func.distinct(Workout.id)).label("workout_count")
                )
                .join(WorkoutExercise, Exercise.id == WorkoutExercise.exercise_id)
                .join(WorkoutSet, WorkoutExercise.id == WorkoutSet.workout_exercise_id)
                .join(Workout, WorkoutExercise.workout_id == Workout.id)
                .where(Workout.user_id == user_id)
                .group_by(Exercise.muscle_group)
            )

            result = await session.execute(stmt)
            muscle_data = result.all()

            if not muscle_data:
                return {"weak_points": [], "recommendations": []}

            muscle_volumes = {}
            total_volume = 0

            for muscle, volume, count in muscle_data:
                muscle_volumes[muscle] = {
                    "volume": volume or 0,
                    "workout_count": count or 0
                }
                total_volume += volume or 0

            # Calculate relative volumes
            weak_points = []
            for muscle, data in muscle_volumes.items():
                relative_volume = (data["volume"] / total_volume * 100) if total_volume > 0 else 0
                data["relative_volume"] = relative_volume

                # Consider a muscle group weak if it's less than expected distribution
                expected_percentage = 100 / len(muscle_volumes)
                if relative_volume < expected_percentage * 0.7:  # 70% of expected
                    weak_points.append({
                        "muscle_group": muscle,
                        "relative_volume": relative_volume,
                        "deficit": expected_percentage - relative_volume
                    })

            # Sort by deficit
            weak_points.sort(key=lambda x: x["deficit"], reverse=True)

            return {
                "muscle_distribution": muscle_volumes,
                "weak_points": weak_points[:3],  # Top 3 weak points
                "total_volume": total_volume
            }

    async def generate_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate AI-powered workout recommendations based on progress"""
        weak_points = await self.identify_weak_points(user_id)
        volume_data = await self.calculate_volume_progression(user_id)

        recommendations = []

        # Recommendations based on weak points
        for weak_point in weak_points.get("weak_points", []):
            muscle = weak_point["muscle_group"]
            deficit = weak_point["deficit"]

            recommendations.append({
                "type": "muscle_balance",
                "priority": "high" if deficit > 10 else "medium",
                "message": f"Increase {muscle} training volume by {deficit:.1f}%",
                "suggestion": f"Add 1-2 more {muscle} exercises to your routine"
            })

        # Recommendations based on volume trend
        trend = volume_data.get("trend", 0)
        if trend < 0:
            recommendations.append({
                "type": "volume_trend",
                "priority": "high",
                "message": "Your training volume is decreasing",
                "suggestion": "Consider increasing sets or weight progressively"
            })
        elif trend < 50:  # Less than 50kg increase per week
            recommendations.append({
                "type": "volume_trend",
                "priority": "medium",
                "message": "Your progression is slowing down",
                "suggestion": "Try adding an extra set to main exercises"
            })

        # General recommendations
        async with get_session() as session:
            # Check workout frequency
            stmt = select(func.count(Workout.id)).where(
                Workout.user_id == user_id,
                Workout.date >= datetime.now() - timedelta(days=7)
            )
            result = await session.execute(stmt)
            weekly_workouts = result.scalar() or 0

            if weekly_workouts < 3:
                recommendations.append({
                    "type": "frequency",
                    "priority": "high",
                    "message": f"Only {weekly_workouts} workouts this week",
                    "suggestion": "Aim for at least 3-4 workouts per week"
                })

        return recommendations

    async def get_personal_records(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all personal records for a user"""
        async with get_session() as session:
            stmt = (
                select(PersonalRecord)
                .where(PersonalRecord.user_id == user_id)
                .options(selectinload(PersonalRecord.exercise))
                .order_by(PersonalRecord.date_achieved.desc())
            )

            result = await session.execute(stmt)
            records = result.scalars().all()

            pr_list = []
            for record in records:
                pr_list.append({
                    "exercise": record.exercise.name,
                    "type": record.record_type,
                    "value": record.value,
                    "date": record.date_achieved
                })

            return pr_list

    async def check_and_update_personal_records(
        self,
        user_id: int,
        workout_id: int
    ) -> List[Dict[str, Any]]:
        """Check if any personal records were broken in a workout"""
        async with get_session() as session:
            # Get workout data
            stmt = (
                select(Workout)
                .where(Workout.id == workout_id)
                .options(
                    selectinload(Workout.exercises)
                    .selectinload(WorkoutExercise.exercise),
                    selectinload(Workout.exercises)
                    .selectinload(WorkoutExercise.sets)
                )
            )

            result = await session.execute(stmt)
            workout = result.scalar_one_or_none()

            if not workout:
                return []

            new_records = []

            for workout_exercise in workout.exercises:
                exercise = workout_exercise.exercise

                for workout_set in workout_exercise.sets:
                    # Check for max weight PR
                    stmt = select(PersonalRecord).where(
                        PersonalRecord.user_id == user_id,
                        PersonalRecord.exercise_id == exercise.id,
                        PersonalRecord.record_type == "MAX_WEIGHT"
                    )
                    result = await session.execute(stmt)
                    weight_pr = result.scalar_one_or_none()

                    if not weight_pr or workout_set.weight > weight_pr.value:
                        if weight_pr:
                            weight_pr.value = workout_set.weight
                            weight_pr.date_achieved = datetime.now()
                            weight_pr.workout_id = workout_id
                        else:
                            weight_pr = PersonalRecord(
                                user_id=user_id,
                                exercise_id=exercise.id,
                                record_type="MAX_WEIGHT",
                                value=workout_set.weight,
                                workout_id=workout_id
                            )
                            session.add(weight_pr)

                        new_records.append({
                            "exercise": exercise.name,
                            "type": "MAX_WEIGHT",
                            "value": workout_set.weight
                        })

                    # Check for max reps PR
                    stmt = select(PersonalRecord).where(
                        PersonalRecord.user_id == user_id,
                        PersonalRecord.exercise_id == exercise.id,
                        PersonalRecord.record_type == "MAX_REPS"
                    )
                    result = await session.execute(stmt)
                    reps_pr = result.scalar_one_or_none()

                    if not reps_pr or workout_set.reps > reps_pr.value:
                        if reps_pr:
                            reps_pr.value = workout_set.reps
                            reps_pr.date_achieved = datetime.now()
                            reps_pr.workout_id = workout_id
                        else:
                            reps_pr = PersonalRecord(
                                user_id=user_id,
                                exercise_id=exercise.id,
                                record_type="MAX_REPS",
                                value=workout_set.reps,
                                workout_id=workout_id
                            )
                            session.add(reps_pr)

                        new_records.append({
                            "exercise": exercise.name,
                            "type": "MAX_REPS",
                            "value": workout_set.reps
                        })

            await session.commit()
            return new_records