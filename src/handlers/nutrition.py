"""Nutrition tracking handlers for the gym bot"""

import logging
from typing import Dict, Any
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date

from src.database.connection import get_session
from src.services.user_service import UserService
from src.services.nutrition_service import nutrition_service
from src.models.nutrition import Food  # Import the Food model directly
from src.locales.translations import i18n

logger = logging.getLogger(__name__)

class NutritionStates(StatesGroup):
    """FSM states for nutrition tracking"""
    waiting_for_search = State()
    waiting_for_portion = State()
    setting_goals = State()
    waiting_for_goal_calories = State()
    waiting_for_goal_protein = State()
    waiting_for_goal_carbs = State()
    waiting_for_goal_fat = State()

def create_nutrition_menu(user_id: int) -> InlineKeyboardMarkup:
    """Create nutrition main menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get("nutrition_add_food", user_id), callback_data="nutrition:add_food")],
        [InlineKeyboardButton(text=i18n.get("nutrition_daily_summary", user_id), callback_data="nutrition:daily_summary")],
        [InlineKeyboardButton(text=i18n.get("nutrition_set_goals", user_id), callback_data="nutrition:set_goals")],
        [InlineKeyboardButton(text=i18n.get("nutrition_view_meals", user_id), callback_data="nutrition:view_meals")],
        [InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="main_menu")]
    ])

def create_meal_type_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create meal type selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get("meal_breakfast", user_id), callback_data="nutrition:meal:breakfast")],
        [InlineKeyboardButton(text=i18n.get("meal_lunch", user_id), callback_data="nutrition:meal:lunch")],
        [InlineKeyboardButton(text=i18n.get("meal_dinner", user_id), callback_data="nutrition:meal:dinner")],
        [InlineKeyboardButton(text=i18n.get("meal_snack", user_id), callback_data="nutrition:meal:snack")],
        [InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="nutrition:menu")]
    ])

def create_food_results_keyboard(foods: list, user_id: int) -> InlineKeyboardMarkup:
    """Create keyboard with food search results"""
    buttons = []
    
    for food in foods[:5]:
        name = food.get('description', 'Unknown food')
        fdc_id = food.get('fdcId')
        display_name = name[:35] + "..." if len(name) > 35 else name
        
        buttons.append([InlineKeyboardButton(
            text=display_name,
            callback_data=f"nutrition:select_food:{fdc_id}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text=i18n.get("btn_back", user_id), 
        callback_data="nutrition:add_food"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_back_keyboard(user_id: int, callback_data: str = "nutrition:menu") -> InlineKeyboardMarkup:
    """Create keyboard with back button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data=callback_data)]
    ])

# Create router
nutrition_router = Router()
user_service = UserService()

@nutrition_router.message(Command("nutrition"))
async def nutrition_command(message: Message):
    """Handle /nutrition command"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        # Ensure user exists
        await user_service.get_or_create_user(
            session, 
            user_id, 
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.language_code or "en"
        )

    welcome_text = i18n.get("nutrition_welcome", user_id)
    keyboard = create_nutrition_menu(user_id)
    
    await message.answer(welcome_text, reply_markup=keyboard)

@nutrition_router.callback_query(F.data == "nutrition:menu")
async def nutrition_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Handle nutrition main menu callback"""
    await state.clear()
    user_id = callback.from_user.id
    
    text = i18n.get("nutrition_main_menu", user_id)
    keyboard = create_nutrition_menu(user_id)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@nutrition_router.callback_query(F.data == "nutrition:add_food")
async def add_food_callback(callback: CallbackQuery):
    """Handle add food callback"""
    user_id = callback.from_user.id
    
    text = i18n.get("nutrition_select_meal_type", user_id)
    keyboard = create_meal_type_keyboard(user_id)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@nutrition_router.callback_query(F.data.startswith("nutrition:meal:"))
async def meal_type_callback(callback: CallbackQuery, state: FSMContext):
    """Handle meal type selection"""
    meal_type = callback.data.split(":")[2]
    user_id = callback.from_user.id
    
    await state.update_data(meal_type=meal_type)
    
    text = i18n.get("nutrition_enter_food_search", user_id, meal_type=i18n.get(f"meal_{meal_type}", user_id))
    keyboard = create_back_keyboard(user_id, "nutrition:add_food")
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(NutritionStates.waiting_for_search)
    await callback.answer()

@nutrition_router.message(NutritionStates.waiting_for_search)
async def handle_food_search(message: Message, state: FSMContext):
    """Handle food search input"""
    query = message.text.strip()
    user_id = message.from_user.id
    
    if not query:
        await message.answer(i18n.get("nutrition_invalid_search", user_id))
        return

    searching_msg = await message.answer(i18n.get("nutrition_searching", user_id))
    
    foods = await nutrition_service.search_food(query)
    
    if not foods:
        await searching_msg.edit_text(
            i18n.get("nutrition_no_results", user_id, query=query),
            reply_markup=create_back_keyboard(user_id, "nutrition:add_food")
        )
        await state.clear()
        return

    response = i18n.get("nutrition_search_results", user_id, query=query)
    keyboard = create_food_results_keyboard(foods, user_id)
    
    await searching_msg.edit_text(response, reply_markup=keyboard)

@nutrition_router.callback_query(F.data.startswith("nutrition:select_food:"))
async def select_food_callback(callback: CallbackQuery, state: FSMContext):
    """Handle food selection - DEBUG VERSION"""
    try:
        fdc_id = int(callback.data.split(":")[2])
        user_id = callback.from_user.id
        
        logger.info(f"User {user_id} selected food with fdc_id: {fdc_id}")
        
        await callback.message.edit_text(i18n.get("nutrition_getting_food_info", user_id))
        
        async with get_session() as session:
            logger.info(f"Calling nutrition_service.get_food_details with fdc_id: {fdc_id}")
            # Get food details using the nutrition service
            food = await nutrition_service.get_food_details(session, fdc_id)
            logger.info(f"get_food_details returned: {food}")
        
        if not food:
            logger.error(f"get_food_details returned None for fdc_id: {fdc_id}")
            await callback.message.edit_text(
                f"❌ Debug: get_food_details returned None for fdc_id {fdc_id}. Check nutrition_service.py",
                reply_markup=create_back_keyboard(user_id, "nutrition:add_food")
            )
            await callback.answer()
            return

        logger.info(f"Food details retrieved: {food.name}, calories: {food.calories_per_100g}")
        
        # Store food ID in state
        await state.update_data(selected_food_id=food.id)
        
        # Show nutrition info and ask for portion
        response = i18n.get("nutrition_food_details", user_id,
                           name=food.name,
                           calories=food.calories_per_100g,
                           protein=food.protein_per_100g,
                           carbs=food.carbs_per_100g,
                           fat=food.fat_per_100g)
        
        await callback.message.edit_text(
            response, 
            reply_markup=create_back_keyboard(user_id, "nutrition:add_food")
        )
        await state.set_state(NutritionStates.waiting_for_portion)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in select_food_callback: {e}", exc_info=True)
        await callback.message.edit_text(
            f"❌ Debug: Exception occurred: {str(e)}",
            reply_markup=create_back_keyboard(user_id, "nutrition:add_food")
        )
        await callback.answer()

@nutrition_router.message(NutritionStates.waiting_for_portion)
async def handle_portion_input(message: Message, state: FSMContext):
    """Handle portion size input"""
    user_id = message.from_user.id
    
    try:
        portion_grams = float(message.text.strip())
        
        if portion_grams <= 0:
            await message.answer(i18n.get("nutrition_invalid_portion", user_id))
            return
        
        data = await state.get_data()
        
        async with get_session() as session:
            # Get user
            user = await user_service.get_user(session, user_id)
            
            # Get food using correct import
            food = await session.get(Food, data['selected_food_id'])
            if not food:
                await message.answer(i18n.get("nutrition_food_not_found", user_id))
                await state.clear()
                return
            
            # Log the meal
            meal_entry = await nutrition_service.log_meal(
                session, user.id, food, data['meal_type'], portion_grams
            )
            
            # Show confirmation
            response = i18n.get("nutrition_meal_logged", user_id,
                               meal_type=i18n.get(f"meal_{data['meal_type']}", user_id),
                               food_name=food.name,
                               portion=portion_grams,
                               calories=meal_entry.calories,
                               protein=meal_entry.protein,
                               carbs=meal_entry.carbs,
                               fat=meal_entry.fat)
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=i18n.get("nutrition_add_more", user_id), callback_data="nutrition:add_food")],
                [InlineKeyboardButton(text=i18n.get("nutrition_view_summary", user_id), callback_data="nutrition:daily_summary")],
                [InlineKeyboardButton(text=i18n.get("nutrition_main_menu", user_id), callback_data="nutrition:menu")]
            ])
            
            await message.answer(response, reply_markup=keyboard)
            await state.clear()
            
    except ValueError:
        await message.answer(i18n.get("nutrition_invalid_number", user_id))
    except Exception as e:
        logger.error(f"Error in handle_portion_input: {e}")
        await message.answer(i18n.get("nutrition_food_info_error", user_id))
        await state.clear()

@nutrition_router.callback_query(F.data == "nutrition:daily_summary")
async def daily_summary_callback(callback: CallbackQuery):
    """Handle daily summary callback"""
    user_id = callback.from_user.id
    
    async with get_session() as session:
        user = await user_service.get_user(session, user_id)
        if not user:
            await callback.message.edit_text(i18n.get("error_user_not_found", user_id))
            return
        
        # Get daily intake
        intake = await nutrition_service.get_daily_intake(session, user.id)
        
        # Get user goals
        goals = await nutrition_service.get_or_create_nutrition_goals(session, user.id)
        
        # Calculate percentages
        cal_percent = (intake['calories'] / goals.daily_calories * 100) if goals.daily_calories > 0 else 0
        protein_percent = (intake['protein'] / goals.daily_protein * 100) if goals.daily_protein > 0 else 0
        carbs_percent = (intake['carbs'] / goals.daily_carbs * 100) if goals.daily_carbs > 0 else 0
        fat_percent = (intake['fat'] / goals.daily_fat * 100) if goals.daily_fat > 0 else 0
        
        response = i18n.get("nutrition_daily_summary_full", user_id,
                           date=date.today().strftime('%B %d, %Y'),
                           calories=intake['calories'],
                           protein=intake['protein'],
                           carbs=intake['carbs'],
                           fat=intake['fat'],
                           cal_percent=cal_percent,
                           protein_percent=protein_percent,
                           carbs_percent=carbs_percent,
                           fat_percent=fat_percent,
                           goal_calories=goals.daily_calories,
                           goal_protein=goals.daily_protein,
                           goal_carbs=goals.daily_carbs,
                           goal_fat=goals.daily_fat)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=i18n.get("nutrition_add_food", user_id), callback_data="nutrition:add_food")],
            [InlineKeyboardButton(text=i18n.get("nutrition_view_meals", user_id), callback_data="nutrition:view_meals")],
            [InlineKeyboardButton(text=i18n.get("nutrition_set_goals", user_id), callback_data="nutrition:set_goals")],
            [InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="nutrition:menu")]
        ])
        
        await callback.message.edit_text(response, reply_markup=keyboard)
    
    await callback.answer()

@nutrition_router.callback_query(F.data == "nutrition:set_goals")
async def set_goals_callback(callback: CallbackQuery, state: FSMContext):
    """Handle set goals callback"""
    user_id = callback.from_user.id
    
    async with get_session() as session:
        user = await user_service.get_user(session, user_id)
        if not user:
            await callback.message.edit_text(i18n.get("error_user_not_found", user_id))
            return
            
        goals = await nutrition_service.get_or_create_nutrition_goals(session, user.id)
        
        response = i18n.get("nutrition_set_goals_start", user_id,
                           calories=goals.daily_calories,
                           protein=goals.daily_protein,
                           carbs=goals.daily_carbs,
                           fat=goals.daily_fat)
        
        await callback.message.edit_text(
            response, 
            reply_markup=create_back_keyboard(user_id, "nutrition:menu")
        )
        await state.set_state(NutritionStates.waiting_for_goal_calories)
    
    await callback.answer()

@nutrition_router.message(NutritionStates.waiting_for_goal_calories)
async def handle_goal_calories(message: Message, state: FSMContext):
    """Handle calorie goal input"""
    user_id = message.from_user.id
    
    try:
        calories = float(message.text.strip())
        
        if calories <= 0 or calories > 10000:  # Reasonable bounds for health
            await message.answer(i18n.get("nutrition_invalid_calories", user_id))
            return
        
        await state.update_data(goal_calories=calories)
        
        await message.answer(i18n.get("nutrition_calories_set", user_id, calories=calories))
        await state.set_state(NutritionStates.waiting_for_goal_protein)
        
    except ValueError:
        await message.answer(i18n.get("nutrition_invalid_number", user_id))

@nutrition_router.message(NutritionStates.waiting_for_goal_protein)
async def handle_goal_protein(message: Message, state: FSMContext):
    """Handle protein goal input"""
    user_id = message.from_user.id
    
    try:
        protein = float(message.text.strip())
        
        if protein <= 0 or protein > 500:  # Reasonable bounds
            await message.answer(i18n.get("nutrition_invalid_protein", user_id))
            return
        
        await state.update_data(goal_protein=protein)
        
        await message.answer(i18n.get("nutrition_protein_set", user_id, protein=protein))
        await state.set_state(NutritionStates.waiting_for_goal_carbs)
        
    except ValueError:
        await message.answer(i18n.get("nutrition_invalid_number", user_id))

@nutrition_router.message(NutritionStates.waiting_for_goal_carbs)
async def handle_goal_carbs(message: Message, state: FSMContext):
    """Handle carbs goal input"""
    user_id = message.from_user.id
    
    try:
        carbs = float(message.text.strip())
        
        if carbs <= 0 or carbs > 1000:  # Reasonable bounds
            await message.answer(i18n.get("nutrition_invalid_carbs", user_id))
            return
        
        await state.update_data(goal_carbs=carbs)
        
        await message.answer(i18n.get("nutrition_carbs_set", user_id, carbs=carbs))
        await state.set_state(NutritionStates.waiting_for_goal_fat)
        
    except ValueError:
        await message.answer(i18n.get("nutrition_invalid_number", user_id))

@nutrition_router.message(NutritionStates.waiting_for_goal_fat)
async def handle_goal_fat(message: Message, state: FSMContext):
    """Handle fat goal input"""
    user_id = message.from_user.id
    
    try:
        fat = float(message.text.strip())
        
        if fat <= 0 or fat > 300:  # Reasonable bounds
            await message.answer(i18n.get("nutrition_invalid_fat", user_id))
            return
        
        data = await state.get_data()
        
        async with get_session() as session:
            user = await user_service.get_user(session, user_id)
            if not user:
                await message.answer(i18n.get("error_user_not_found", user_id))
                await state.clear()
                return
            
            # Save all goals to database
            await nutrition_service.update_nutrition_goals(
                session, 
                user.id,
                data['goal_calories'], 
                data['goal_protein'], 
                data['goal_carbs'], 
                fat
            )
            
            response = i18n.get("nutrition_goals_saved", user_id,
                               calories=data['goal_calories'],
                               protein=data['goal_protein'],
                               carbs=data['goal_carbs'],
                               fat=fat)
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=i18n.get("nutrition_add_food", user_id), callback_data="nutrition:add_food")],
                [InlineKeyboardButton(text=i18n.get("nutrition_daily_summary", user_id), callback_data="nutrition:daily_summary")],
                [InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="nutrition:menu")]
            ])
            
            await message.answer(response, reply_markup=keyboard)
            await state.clear()
            
    except ValueError:
        await message.answer(i18n.get("nutrition_invalid_number", user_id))

@nutrition_router.callback_query(F.data == "nutrition:view_meals")
async def view_meals_callback(callback: CallbackQuery):
    """Handle view meals callback"""
    user_id = callback.from_user.id
    
    async with get_session() as session:
        user = await user_service.get_user(session, user_id)
        if not user:
            await callback.message.edit_text(i18n.get("error_user_not_found", user_id))
            return
        
        meals_by_type = await nutrition_service.get_meals_by_type(session, user.id)
        
        # Check if any meals exist
        total_meals = sum(len(meals) for meals in meals_by_type.values())
        
        if total_meals == 0:
            response = i18n.get("nutrition_no_meals_today", user_id)
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=i18n.get("nutrition_add_food", user_id), callback_data="nutrition:add_food")],
                [InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="nutrition:menu")]
            ])
        else:
            response = i18n.get("nutrition_todays_meals", user_id, date=date.today().strftime('%B %d, %Y'))
            response += "\n\n"
            
            meal_emojis = {
                "breakfast": "🥞", 
                "lunch": "🥗", 
                "dinner": "🍽️", 
                "snack": "🍎"
            }
            
            for meal_type, meals in meals_by_type.items():
                if meals:
                    response += f"\n{meal_emojis[meal_type]} **{i18n.get(f'meal_{meal_type}', user_id)}:**\n"
                    
                    for meal in meals:
                        response += f"• {meal.food.name} ({meal.portion_grams:.0f}g)\n"
                        response += f"  {meal.calories:.0f} kcal | P: {meal.protein:.1f}g | C: {meal.carbs:.1f}g | F: {meal.fat:.1f}g\n"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=i18n.get("nutrition_add_food", user_id), callback_data="nutrition:add_food")],
                [InlineKeyboardButton(text=i18n.get("nutrition_daily_summary", user_id), callback_data="nutrition:daily_summary")],
                [InlineKeyboardButton(text=i18n.get("btn_back", user_id), callback_data="nutrition:menu")]
            ])
        
        await callback.message.edit_text(response, reply_markup=keyboard, parse_mode="Markdown")
    
    await callback.answer()

def register_nutrition_handlers(dp):
    """Register nutrition handlers with the dispatcher"""
    dp.include_router(nutrition_router)