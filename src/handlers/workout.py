"""Workout tracking handlers"""

import logging
from datetime import datetime
from typing import List, Optional
from aiogram import Router, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from src.services.workout_service import WorkoutService
from src.services.exercise_service import ExerciseService
from src.services.user_service import UserService
from src.locales.translations import i18n
from src.database.connection import get_session

logger = logging.getLogger(__name__)

class WorkoutStates(StatesGroup):
    """FSM states for workout logging conversation"""
    selecting_exercise = State()
    searching_exercise = State()
    entering_sets = State()
    entering_reps = State()
    entering_weight = State()
    confirming = State()

def register_workout_handlers(dp: Dispatcher):
    """Register workout tracking handlers"""
    router = Router()

    @router.message(Command("log"))
    async def cmd_log_workout(message: Message, state: FSMContext):
        """Start workout logging conversation"""
        user_id = message.from_user.id
        logger.info(f"User {user_id} started workout logging")

        async with get_session() as session:
            # Check if user exists
            user_service = UserService()
            user = await user_service.get_user(session, user_id)
            if not user:
                await message.answer(i18n.get("error_not_found", user_id))
                return

            # Get exercises from database
            exercise_service = ExerciseService()
            exercises = await exercise_service.get_all_exercises(session)

            if not exercises:
                await message.answer("❌ No exercises found in database. Please contact support.")
                return

            # Create exercise selection keyboard
            keyboard = InlineKeyboardMarkup(inline_keyboard=[])

            # Group exercises by category
            categories = {}
            for ex in exercises:
                if ex.category not in categories:
                    categories[ex.category] = []
                categories[ex.category].append(ex)

            # Add category buttons
            for category, exs in categories.items():
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(
                        text=f"💪 {category} ({len(exs)} exercises)",
                        callback_data=f"cat:{category}"
                    )
                ])

            # Add search option
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="🔍 Search by name", callback_data="search:exercise")
            ])

            await state.set_state(WorkoutStates.selecting_exercise)
            await state.update_data(user_id=user.id)

            text = i18n.get("select_exercise", user_id)
            await message.answer(text, reply_markup=keyboard)

    @router.callback_query(StateFilter(WorkoutStates.selecting_exercise), F.data.startswith("cat:"))
    async def show_category_exercises(callback: CallbackQuery, state: FSMContext):
        """Show exercises in selected category"""
        category = callback.data.split(":", 1)[1]
        user_id = callback.from_user.id

        async with get_session() as session:
            exercise_service = ExerciseService()
            exercises = await exercise_service.get_exercises_by_category(session, category)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[])

            # Add exercise buttons (max 10 per page for now)
            for ex in exercises[:10]:
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(
                        text=f"{ex.name}",
                        callback_data=f"ex:{ex.id}"
                    )
                ])

            # Add back button
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="⬅️ Back", callback_data="back:categories")
            ])

            await callback.message.edit_text(
                f"Select exercise from {category}:",
                reply_markup=keyboard
            )

    @router.callback_query(StateFilter(WorkoutStates.selecting_exercise), F.data == "back:categories")
    async def back_to_categories(callback: CallbackQuery, state: FSMContext):
        """Go back to category selection"""
        await cmd_log_workout(callback.message, state)

    @router.callback_query(StateFilter(WorkoutStates.selecting_exercise), F.data == "search:exercise")
    async def search_exercise(callback: CallbackQuery, state: FSMContext):
        """Start exercise search"""
        user_id = callback.from_user.id
        await state.set_state(WorkoutStates.searching_exercise)
        await callback.message.edit_text(
            "🔍 Type the exercise name (or part of it):\n\nFor example: bench, squat, curl"
        )

    @router.message(StateFilter(WorkoutStates.searching_exercise))
    async def process_exercise_search(message: Message, state: FSMContext):
        """Process exercise search query"""
        query = message.text.strip()
        user_id = message.from_user.id

        async with get_session() as session:
            exercise_service = ExerciseService()
            exercises = await exercise_service.search_exercises(session, query)

            if not exercises:
                await message.answer(
                    "❌ No exercises found. Try different keywords or /cancel to stop."
                )
                return

            # Show search results
            keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            for ex in exercises[:8]:  # Show max 8 results
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(
                        text=f"{ex.name} ({ex.category})",
                        callback_data=f"ex:{ex.id}"
                    )
                ])

            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="🔍 Search again", callback_data="search:exercise"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
            ])

            await state.set_state(WorkoutStates.selecting_exercise)
            await message.answer(
                f"Found {len(exercises)} exercises:",
                reply_markup=keyboard
            )

    @router.callback_query(StateFilter(WorkoutStates.selecting_exercise), F.data.startswith("ex:"))
    async def process_exercise_selection(callback: CallbackQuery, state: FSMContext):
        """Process exercise selection"""
        exercise_id = int(callback.data.split(":", 1)[1])
        user_id = callback.from_user.id

        async with get_session() as session:
            exercise_service = ExerciseService()
            exercise = await exercise_service.get_exercise_by_id(session, exercise_id)

            if not exercise:
                await callback.answer("Exercise not found!")
                return

            # Store exercise in state
            await state.update_data(exercise_id=exercise_id, exercise_name=exercise.name)
            await state.set_state(WorkoutStates.entering_sets)

            # Ask for number of sets
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="1", callback_data="sets:1"),
                    InlineKeyboardButton(text="2", callback_data="sets:2"),
                    InlineKeyboardButton(text="3", callback_data="sets:3"),
                ],
                [
                    InlineKeyboardButton(text="4", callback_data="sets:4"),
                    InlineKeyboardButton(text="5", callback_data="sets:5"),
                    InlineKeyboardButton(text="6", callback_data="sets:6"),
                ],
                [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
            ])

            await callback.message.edit_text(
                f"📝 {exercise.name}\n\n" + i18n.get("enter_sets", user_id),
                reply_markup=keyboard
            )

    @router.callback_query(StateFilter(WorkoutStates.entering_sets), F.data.startswith("sets:"))
    async def process_sets_selection(callback: CallbackQuery, state: FSMContext):
        """Process number of sets selection"""
        num_sets = int(callback.data.split(":", 1)[1])
        user_id = callback.from_user.id

        await state.update_data(num_sets=num_sets, current_set=1, sets_data=[])
        await state.set_state(WorkoutStates.entering_reps)

        data = await state.get_data()
        text = f"📝 {data['exercise_name']} - Set 1/{num_sets}\n\n"
        text += i18n.get("enter_reps", user_id, set_number=1)

        await callback.message.edit_text(text)
        await callback.answer()

    @router.message(StateFilter(WorkoutStates.entering_reps))
    async def process_reps_input(message: Message, state: FSMContext):
        """Process reps input"""
        try:
            reps = int(message.text.strip())
            if reps <= 0 or reps > 1000:
                raise ValueError()
        except ValueError:
            await message.answer("❌ Please enter a valid number of reps (1-1000)")
            return

        user_id = message.from_user.id
        await state.update_data(current_reps=reps)
        await state.set_state(WorkoutStates.entering_weight)

        data = await state.get_data()
        text = f"📝 {data['exercise_name']} - Set {data['current_set']}/{data['num_sets']}\n"
        text += f"Reps: {reps}\n\n"
        text += i18n.get("enter_weight", user_id, set_number=data['current_set'])

        await message.answer(text)

    @router.message(StateFilter(WorkoutStates.entering_weight))
    async def process_weight_input(message: Message, state: FSMContext):
        """Process weight input"""
        try:
            weight = float(message.text.strip())
            if weight < 0 or weight > 1000:
                raise ValueError()
        except ValueError:
            await message.answer("❌ Please enter a valid weight (0-1000 kg)")
            return

        data = await state.get_data()
        user_id = message.from_user.id

        # Store set data
        sets_data = data.get('sets_data', [])
        sets_data.append({
            'set_number': data['current_set'],
            'reps': data['current_reps'],
            'weight': weight
        })

        current_set = data['current_set']
        num_sets = data['num_sets']

        if current_set < num_sets:
            # More sets to enter
            await state.update_data(
                current_set=current_set + 1,
                sets_data=sets_data
            )
            await state.set_state(WorkoutStates.entering_reps)

            text = f"📝 {data['exercise_name']} - Set {current_set + 1}/{num_sets}\n\n"
            text += i18n.get("enter_reps", user_id, set_number=current_set + 1)
            await message.answer(text)
        else:
            # All sets entered, save workout
            await state.update_data(sets_data=sets_data)
            await save_workout(message, state)

    async def save_workout(message: Message, state: FSMContext):
        """Save the completed workout"""
        data = await state.get_data()
        user_id = message.from_user.id

        async with get_session() as session:
            workout_service = WorkoutService()
            user_service = UserService()

            # Get user
            user = await user_service.get_user(session, user_id)
            if not user:
                await message.answer("❌ User not found")
                await state.clear()
                return

            # Create workout
            workout = await workout_service.create_workout(
                session=session,
                user_id=user.id,
                exercise_id=data['exercise_id'],
                sets_data=data['sets_data']
            )

            if workout:
                # Calculate total volume
                total_volume = sum(s['reps'] * s['weight'] for s in data['sets_data'])

                summary = f"✅ <b>Workout Saved!</b>\n\n"
                summary += f"📝 {data['exercise_name']}\n"
                summary += f"📊 {data['num_sets']} sets\n"
                summary += f"💪 Total volume: {total_volume:.0f} kg\n\n"

                for s in data['sets_data']:
                    summary += f"Set {s['set_number']}: {s['reps']} × {s['weight']} kg\n"

                await message.answer(summary)
                logger.info(f"User {user_id} logged workout: {data['exercise_name']}")
            else:
                await message.answer("❌ Failed to save workout")

        await state.clear()

    @router.callback_query(F.data == "cancel")
    async def cancel_workout(callback: CallbackQuery, state: FSMContext):
        """Cancel workout logging"""
        await state.clear()
        await callback.message.edit_text("❌ Workout logging cancelled")
        await callback.answer()

    @router.message(Command("cancel"))
    async def cmd_cancel(message: Message, state: FSMContext):
        """Cancel any ongoing conversation"""
        current_state = await state.get_state()
        if current_state:
            await state.clear()
            await message.answer("❌ Operation cancelled")
        else:
            await message.answer("Nothing to cancel")

    dp.include_router(router)