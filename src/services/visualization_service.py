import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.models import Workout, WorkoutExercise, WorkoutSet, Exercise, ProgressRecord
from src.database.connection import get_session

logger = logging.getLogger(__name__)

# Set style for all plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class AdvancedVisualization:
    """Advanced visualization system for progress tracking"""

    def __init__(self):
        self.figure_size = (15, 12)
        self.dpi = 100

    async def create_multi_panel_dashboard(
        self,
        user_id: int,
        exercise_id: Optional[int] = None
    ) -> bytes:
        """Create comprehensive 4-panel progress dashboard"""
        fig, axes = plt.subplots(2, 2, figsize=self.figure_size, dpi=self.dpi)
        fig.suptitle('Workout Progress Dashboard', fontsize=16, fontweight='bold')

        # Panel 1: Weight progression
        await self._plot_weight_progression(axes[0, 0], user_id, exercise_id)

        # Panel 2: Volume heatmap
        await self._plot_volume_heatmap(axes[0, 1], user_id)

        # Panel 3: 1RM progression
        await self._plot_1rm_progression(axes[1, 0], user_id, exercise_id)

        # Panel 4: Muscle group distribution
        await self._plot_muscle_distribution(axes[1, 1], user_id)

        plt.tight_layout()
        return self._fig_to_bytes(fig)

    async def _plot_weight_progression(
        self,
        ax: plt.Axes,
        user_id: int,
        exercise_id: Optional[int]
    ):
        """Plot weight progression with polynomial fit"""
        async with get_session() as session:
            if exercise_id:
                stmt = (
                    select(
                        Workout.date,
                        func.max(WorkoutSet.weight).label("max_weight"),
                        func.avg(WorkoutSet.weight).label("avg_weight")
                    )
                    .join(WorkoutExercise, Workout.id == WorkoutExercise.workout_id)
                    .join(WorkoutSet, WorkoutExercise.id == WorkoutSet.workout_exercise_id)
                    .where(
                        Workout.user_id == user_id,
                        WorkoutExercise.exercise_id == exercise_id
                    )
                    .group_by(Workout.date)
                    .order_by(Workout.date)
                )
            else:
                stmt = (
                    select(
                        Workout.date,
                        func.max(WorkoutSet.weight).label("max_weight"),
                        func.avg(WorkoutSet.weight).label("avg_weight")
                    )
                    .join(WorkoutExercise, Workout.id == WorkoutExercise.workout_id)
                    .join(WorkoutSet, WorkoutExercise.id == WorkoutSet.workout_exercise_id)
                    .where(Workout.user_id == user_id)
                    .group_by(Workout.date)
                    .order_by(Workout.date)
                )

            result = await session.execute(stmt)
            data = result.all()

            if not data:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
                ax.set_title('Weight Progression')
                return

            dates = [d[0] for d in data]
            max_weights = [d[1] for d in data]
            avg_weights = [d[2] for d in data]

            # Plot actual data
            ax.plot(dates, max_weights, 'o-', label='Max Weight', linewidth=2, markersize=8)
            ax.plot(dates, avg_weights, 's-', label='Avg Weight', linewidth=2, markersize=6, alpha=0.7)

            # Add polynomial trend line if enough data
            if len(dates) > 3:
                x = np.arange(len(dates))
                z = np.polyfit(x, max_weights, 2)
                p = np.poly1d(z)
                ax.plot(dates, p(x), '--', label='Trend', linewidth=2, alpha=0.5)

            ax.set_title('Weight Progression Over Time', fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Weight (kg)')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)

            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    async def _plot_volume_heatmap(self, ax: plt.Axes, user_id: int):
        """Plot weekly volume heatmap"""
        async with get_session() as session:
            # Get last 12 weeks of data
            start_date = datetime.now() - timedelta(weeks=12)
            stmt = (
                select(
                    Workout.date,
                    func.sum(WorkoutSet.weight * WorkoutSet.reps).label("volume")
                )
                .join(WorkoutExercise, Workout.id == WorkoutExercise.workout_id)
                .join(WorkoutSet, WorkoutExercise.id == WorkoutSet.workout_exercise_id)
                .where(
                    Workout.user_id == user_id,
                    Workout.date >= start_date
                )
                .group_by(Workout.date)
            )

            result = await session.execute(stmt)
            data = result.all()

            if not data:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
                ax.set_title('Volume Heatmap')
                return

            # Create DataFrame for heatmap
            df = pd.DataFrame(data, columns=['date', 'volume'])
            df['week'] = df['date'].apply(lambda x: x.isocalendar()[1])
            df['day'] = df['date'].apply(lambda x: x.weekday())

            # Pivot for heatmap
            pivot_table = df.pivot_table(
                values='volume',
                index='week',
                columns='day',
                aggfunc='sum',
                fill_value=0
            )

            # Create heatmap
            sns.heatmap(
                pivot_table,
                ax=ax,
                cmap='YlOrRd',
                annot=False,
                fmt='.0f',
                cbar_kws={'label': 'Volume (kg)'},
                linewidths=0.5
            )

            ax.set_title('Weekly Training Volume Heatmap', fontweight='bold')
            ax.set_xlabel('Day of Week')
            ax.set_ylabel('Week Number')
            ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

    async def _plot_1rm_progression(
        self,
        ax: plt.Axes,
        user_id: int,
        exercise_id: Optional[int]
    ):
        """Plot estimated 1RM progression with confidence intervals"""
        async with get_session() as session:
            if exercise_id:
                stmt = (
                    select(
                        Workout.date,
                        WorkoutSet.weight,
                        WorkoutSet.reps
                    )
                    .join(WorkoutExercise, Workout.id == WorkoutExercise.workout_id)
                    .join(WorkoutSet, WorkoutExercise.id == WorkoutSet.workout_exercise_id)
                    .where(
                        Workout.user_id == user_id,
                        WorkoutExercise.exercise_id == exercise_id
                    )
                    .order_by(Workout.date)
                )
            else:
                # Get the most frequent exercise
                stmt = (
                    select(
                        Workout.date,
                        WorkoutSet.weight,
                        WorkoutSet.reps
                    )
                    .join(WorkoutExercise, Workout.id == WorkoutExercise.workout_id)
                    .join(WorkoutSet, WorkoutExercise.id == WorkoutSet.workout_exercise_id)
                    .where(Workout.user_id == user_id)
                    .order_by(Workout.date)
                    .limit(100)
                )

            result = await session.execute(stmt)
            data = result.all()

            if not data:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
                ax.set_title('1RM Progression')
                return

            # Calculate 1RM for each set using Brzycki formula
            one_rms_by_date = {}
            for date, weight, reps in data:
                if reps < 37:
                    one_rm = weight * (36 / (37 - reps))
                    if date not in one_rms_by_date:
                        one_rms_by_date[date] = []
                    one_rms_by_date[date].append(one_rm)

            if not one_rms_by_date:
                ax.text(0.5, 0.5, 'Insufficient data for 1RM calculation', ha='center', va='center')
                ax.set_title('1RM Progression')
                return

            dates = sorted(one_rms_by_date.keys())
            mean_1rms = [np.mean(one_rms_by_date[d]) for d in dates]
            std_1rms = [np.std(one_rms_by_date[d]) for d in dates]

            # Plot with confidence intervals
            ax.plot(dates, mean_1rms, 'o-', linewidth=2, markersize=8, label='Estimated 1RM')

            # Add confidence bands
            lower_bound = [m - s for m, s in zip(mean_1rms, std_1rms)]
            upper_bound = [m + s for m, s in zip(mean_1rms, std_1rms)]
            ax.fill_between(dates, lower_bound, upper_bound, alpha=0.3, label='Confidence Interval')

            ax.set_title('Estimated 1RM Progression', fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('1RM (kg)')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)

            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    async def _plot_muscle_distribution(self, ax: plt.Axes, user_id: int):
        """Plot muscle group volume distribution"""
        async with get_session() as session:
            stmt = (
                select(
                    Exercise.muscle_group,
                    func.sum(WorkoutSet.weight * WorkoutSet.reps).label("total_volume")
                )
                .join(WorkoutExercise, Exercise.id == WorkoutExercise.exercise_id)
                .join(WorkoutSet, WorkoutExercise.id == WorkoutSet.workout_exercise_id)
                .join(Workout, WorkoutExercise.workout_id == Workout.id)
                .where(Workout.user_id == user_id)
                .group_by(Exercise.muscle_group)
                .order_by(func.sum(WorkoutSet.weight * WorkoutSet.reps).desc())
            )

            result = await session.execute(stmt)
            data = result.all()

            if not data:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
                ax.set_title('Muscle Group Distribution')
                return

            muscle_groups = [d[0] for d in data[:8]]  # Top 8 muscle groups
            volumes = [d[1] for d in data[:8]]

            # Create pie chart
            colors = sns.color_palette('husl', len(muscle_groups))
            wedges, texts, autotexts = ax.pie(
                volumes,
                labels=muscle_groups,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )

            # Beautify the plot
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)

            ax.set_title('Training Volume by Muscle Group', fontweight='bold')

    def _fig_to_bytes(self, fig: plt.Figure) -> bytes:
        """Convert matplotlib figure to bytes"""
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=self.dpi)
        buf.seek(0)
        plt.close(fig)
        return buf.getvalue()

    async def create_progress_chart(
        self,
        user_id: int,
        exercise_id: int,
        weeks: int = 12
    ) -> bytes:
        """Create a simple progress chart for a specific exercise"""
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)

        async with get_session() as session:
            start_date = datetime.now() - timedelta(weeks=weeks)
            stmt = (
                select(
                    Workout.date,
                    func.max(WorkoutSet.weight).label("max_weight"),
                    func.sum(WorkoutSet.weight * WorkoutSet.reps).label("volume")
                )
                .join(WorkoutExercise, Workout.id == WorkoutExercise.workout_id)
                .join(WorkoutSet, WorkoutExercise.id == WorkoutSet.workout_exercise_id)
                .where(
                    Workout.user_id == user_id,
                    WorkoutExercise.exercise_id == exercise_id,
                    Workout.date >= start_date
                )
                .group_by(Workout.date)
                .order_by(Workout.date)
            )

            result = await session.execute(stmt)
            data = result.all()

            if not data:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)
                ax.set_title('Progress Chart')
            else:
                dates = [d[0] for d in data]
                weights = [d[1] for d in data]
                volumes = [d[2] for d in data]

                # Create dual axis
                ax2 = ax.twinx()

                # Plot weight on primary axis
                line1 = ax.plot(dates, weights, 'b-o', linewidth=2, markersize=8, label='Max Weight')
                ax.set_xlabel('Date', fontsize=12)
                ax.set_ylabel('Weight (kg)', color='b', fontsize=12)
                ax.tick_params(axis='y', labelcolor='b')

                # Plot volume on secondary axis
                line2 = ax2.plot(dates, volumes, 'r-s', linewidth=2, markersize=6, label='Total Volume', alpha=0.7)
                ax2.set_ylabel('Volume (kg)', color='r', fontsize=12)
                ax2.tick_params(axis='y', labelcolor='r')

                # Add trend line
                if len(dates) > 2:
                    x = np.arange(len(dates))
                    z = np.polyfit(x, weights, 1)
                    p = np.poly1d(z)
                    ax.plot(dates, p(x), 'b--', alpha=0.5, linewidth=1)

                # Get exercise name
                stmt = select(Exercise.name).where(Exercise.id == exercise_id)
                result = await session.execute(stmt)
                exercise_name = result.scalar() or "Exercise"

                ax.set_title(f'{exercise_name} Progress Chart', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)

                # Format x-axis
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

                # Add legend
                lines = line1 + line2
                labels = [l.get_label() for l in lines]
                ax.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        return self._fig_to_bytes(fig)

    async def create_body_composition_chart(
        self,
        user_id: int,
        weeks: int = 12
    ) -> bytes:
        """Create body composition tracking chart"""
        fig, axes = plt.subplots(2, 1, figsize=(10, 8), dpi=self.dpi)

        async with get_session() as session:
            start_date = datetime.now() - timedelta(weeks=weeks)
            stmt = (
                select(ProgressRecord)
                .where(
                    ProgressRecord.user_id == user_id,
                    ProgressRecord.date >= start_date,
                    ProgressRecord.body_weight.isnot(None)
                )
                .order_by(ProgressRecord.date)
            )

            result = await session.execute(stmt)
            records = result.scalars().all()

            if not records:
                for ax in axes:
                    ax.text(0.5, 0.5, 'No body composition data available', ha='center', va='center')
                    ax.set_title('Body Composition')
            else:
                dates = [r.date for r in records]
                weights = [r.body_weight for r in records if r.body_weight]
                body_fat = [r.body_fat_percentage for r in records if r.body_fat_percentage]

                # Plot body weight
                if weights:
                    axes[0].plot(dates[:len(weights)], weights, 'g-o', linewidth=2, markersize=8)
                    axes[0].set_title('Body Weight Tracking', fontweight='bold')
                    axes[0].set_ylabel('Weight (kg)')
                    axes[0].grid(True, alpha=0.3)

                    # Add trend line
                    if len(weights) > 2:
                        x = np.arange(len(weights))
                        z = np.polyfit(x, weights, 1)
                        p = np.poly1d(z)
                        axes[0].plot(dates[:len(weights)], p(x), 'g--', alpha=0.5)

                # Plot body fat percentage
                if body_fat:
                    axes[1].plot(dates[:len(body_fat)], body_fat, 'orange', marker='o', linewidth=2, markersize=8)
                    axes[1].set_title('Body Fat Percentage', fontweight='bold')
                    axes[1].set_ylabel('Body Fat (%)')
                    axes[1].set_xlabel('Date')
                    axes[1].grid(True, alpha=0.3)

                # Format x-axis for both plots
                for ax in axes:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        return self._fig_to_bytes(fig)