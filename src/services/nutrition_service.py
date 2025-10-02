"""Nutrition service for managing food data and USDA API integration"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, date
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from src.models.nutrition import Food, NutritionGoals, MealEntry
from src.models.user import User

logger = logging.getLogger(__name__)

class NutritionService:
    """Service for nutrition-related operations"""

    def __init__(self):
        # USDA API configuration
        self.usda_api_key = os.getenv("USDA_API_KEY", "3X3lZVkwbI7csqXUY0fOxkKm1bdBN8OeJSwZX74y")
        self.usda_base_url = "https://api.nal.usda.gov/fdc/v1"
        self.session: Optional[aiohttp.ClientSession] = None

    async def create_session(self):
        """Create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def search_food(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for food using USDA API"""
        if not self.session:
            await self.create_session()

        url = f"{self.usda_base_url}/foods/search"
        params = {
            "api_key": self.usda_api_key,
            "query": query,
            "pageSize": limit,
            "dataType": ["Foundation", "SR Legacy"]
        }

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('foods', [])
                else:
                    logger.error(f"USDA API request failed with status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error searching food: {e}")
            return []

    async def get_food_details(self, session: AsyncSession, fdc_id: int) -> Optional[Food]:
        """Get detailed food information, from cache or API"""
        # First check cache
        stmt = select(Food).where(Food.fdc_id == fdc_id)
        result = await session.execute(stmt)
        cached_food = result.scalar_one_or_none()

        if cached_food:
            return cached_food

        # If not cached, fetch from API
        if not self.session:
            await self.create_session()

        url = f"{self.usda_base_url}/food/{fdc_id}"
        params = {"api_key": self.usda_api_key}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract and format nutrition data
                    food_data = self._extract_nutrition_data(data)
                    
                    # Cache the food data
                    food = Food(**food_data)
                    session.add(food)
                    await session.commit()
                    await session.refresh(food)
                    
                    return food
                else:
                    logger.error(f"USDA API request failed with status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting food details: {e}")
            return None

    def _extract_nutrition_data(self, api_data: Dict) -> Dict:
        """Extract nutrition data from USDA API response"""
        food_data = {
            'fdc_id': api_data.get('fdcId'),
            'name': api_data.get('description', 'Unknown food'),
            'calories_per_100g': 0,
            'protein_per_100g': 0,
            'carbs_per_100g': 0,
            'fat_per_100g': 0,
            'fiber_per_100g': 0,
            'sodium_per_100g': 0
        }

        nutrients = api_data.get('foodNutrients', [])

        for nutrient in nutrients:
            nutrient_id = nutrient.get('nutrient', {}).get('id', 0)
            value = nutrient.get('amount', 0)

            if nutrient_id == 1008:  # Energy (kcal)
                food_data['calories_per_100g'] = value
            elif nutrient_id == 1003:  # Protein
                food_data['protein_per_100g'] = value
            elif nutrient_id == 1005:  # Carbohydrates
                food_data['carbs_per_100g'] = value
            elif nutrient_id == 1004:  # Total lipid (fat)
                food_data['fat_per_100g'] = value
            elif nutrient_id == 1079:  # Fiber
                food_data['fiber_per_100g'] = value
            elif nutrient_id == 1093:  # Sodium
                food_data['sodium_per_100g'] = value / 1000  # Convert mg to g

        return food_data

    async def get_or_create_nutrition_goals(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> NutritionGoals:
        """Get user's nutrition goals or create default ones"""
        stmt = select(NutritionGoals).where(NutritionGoals.user_id == user_id)
        result = await session.execute(stmt)
        goals = result.scalar_one_or_none()

        if not goals:
            goals = NutritionGoals(user_id=user_id)
            session.add(goals)
            await session.commit()
            await session.refresh(goals)

        return goals

    async def update_nutrition_goals(
        self,
        session: AsyncSession,
        user_id: int,
        calories: float,
        protein: float,
        carbs: float,
        fat: float
    ) -> NutritionGoals:
        """Update user's nutrition goals"""
        goals = await self.get_or_create_nutrition_goals(session, user_id)
        
        goals.daily_calories = calories
        goals.daily_protein = protein
        goals.daily_carbs = carbs
        goals.daily_fat = fat
        goals.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(goals)
        return goals

    async def log_meal(
        self,
        session: AsyncSession,
        user_id: int,
        food: Food,
        meal_type: str,
        portion_grams: float
    ) -> MealEntry:
        """Log a meal entry"""
        # Calculate nutrition for the specified portion
        multiplier = portion_grams / 100

        calories = food.calories_per_100g * multiplier
        protein = food.protein_per_100g * multiplier
        carbs = food.carbs_per_100g * multiplier
        fat = food.fat_per_100g * multiplier

        meal_entry = MealEntry(
            user_id=user_id,
            food_id=food.id,
            date=date.today(),
            meal_type=meal_type,
            portion_grams=portion_grams,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat
        )

        session.add(meal_entry)
        await session.commit()
        await session.refresh(meal_entry)
        return meal_entry

    async def get_daily_intake(
        self, 
        session: AsyncSession, 
        user_id: int, 
        target_date: date = None
    ) -> Dict[str, float]:
        """Get user's daily nutritional intake"""
        if target_date is None:
            target_date = date.today()

        stmt = select(
            func.sum(MealEntry.calories).label('total_calories'),
            func.sum(MealEntry.protein).label('total_protein'),
            func.sum(MealEntry.carbs).label('total_carbs'),
            func.sum(MealEntry.fat).label('total_fat')
        ).where(
            and_(
                MealEntry.user_id == user_id,
                MealEntry.date == target_date
            )
        )

        result = await session.execute(stmt)
        row = result.first()

        return {
            'calories': row.total_calories or 0,
            'protein': row.total_protein or 0,
            'carbs': row.total_carbs or 0,
            'fat': row.total_fat or 0
        }

    async def get_daily_meals(
        self, 
        session: AsyncSession, 
        user_id: int, 
        target_date: date = None
    ) -> List[MealEntry]:
        """Get user's meals for a specific date"""
        if target_date is None:
            target_date = date.today()

        stmt = select(MealEntry).options(
            selectinload(MealEntry.food)
        ).where(
            and_(
                MealEntry.user_id == user_id,
                MealEntry.date == target_date
            )
        ).order_by(MealEntry.logged_at.desc())

        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_meals_by_type(
        self, 
        session: AsyncSession, 
        user_id: int, 
        target_date: date = None
    ) -> Dict[str, List[MealEntry]]:
        """Get user's meals grouped by meal type"""
        meals = await self.get_daily_meals(session, user_id, target_date)
        
        grouped = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': []
        }

        for meal in meals:
            if meal.meal_type in grouped:
                grouped[meal.meal_type].append(meal)

        return grouped

# Global nutrition service instance
nutrition_service = NutritionService()