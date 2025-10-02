from sqlalchemy import Column, Integer, String, DateTime, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date

from src.database.connection import Base

class Food(Base):
    """Food item from USDA database"""
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    fdc_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    
    # Nutrition per 100g
    calories_per_100g = Column(Float, default=0.0, nullable=False)
    protein_per_100g = Column(Float, default=0.0, nullable=False)
    carbs_per_100g = Column(Float, default=0.0, nullable=False)
    fat_per_100g = Column(Float, default=0.0, nullable=False)
    fiber_per_100g = Column(Float, default=0.0, nullable=False)
    sodium_per_100g = Column(Float, default=0.0, nullable=False)  # in grams
    
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    meal_entries = relationship("MealEntry", back_populates="food")

    def __repr__(self):
        return f"<Food(fdc_id={self.fdc_id}, name={self.name})>"


class NutritionGoals(Base):
    """User's daily nutrition goals"""
    __tablename__ = "nutrition_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Daily targets
    daily_calories = Column(Float, default=2000.0, nullable=False)
    daily_protein = Column(Float, default=150.0, nullable=False)
    daily_carbs = Column(Float, default=250.0, nullable=False)
    daily_fat = Column(Float, default=70.0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="nutrition_goals")

    def __repr__(self):
        return f"<NutritionGoals(user_id={self.user_id}, calories={self.daily_calories})>"


class MealEntry(Base):
    """Individual meal entry"""
    __tablename__ = "meal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    
    date = Column(Date, default=date.today, nullable=False)
    meal_type = Column(String, nullable=False)  # breakfast, lunch, dinner, snack
    
    # Portion details
    portion_grams = Column(Float, nullable=False)
    
    # Calculated nutrition for this portion
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="meal_entries")
    food = relationship("Food", back_populates="meal_entries")

    def __repr__(self):
        return f"<MealEntry(user_id={self.user_id}, food={self.food.name if self.food else 'None'}, portion={self.portion_grams}g)>"