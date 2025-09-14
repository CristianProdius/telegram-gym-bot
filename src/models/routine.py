from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.connection import Base

class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # PPL, Upper/Lower, Full Body, etc.
    difficulty = Column(String, default="intermediate")  # beginner, intermediate, advanced
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # JSON field for flexible metadata
    meta_data = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="routines")
    workouts = relationship("Workout", back_populates="routine")
    routine_exercises = relationship("RoutineExercise", back_populates="routine", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Routine(name={self.name}, user_id={self.user_id})>"

class RoutineExercise(Base):
    __tablename__ = "routine_exercises"

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey("routines.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    day = Column(Integer, nullable=True)  # Day of the week (1-7) or workout day number
    order = Column(Integer, nullable=False, default=0)

    # Target sets and reps
    target_sets = Column(Integer, nullable=True)
    target_reps_min = Column(Integer, nullable=True)
    target_reps_max = Column(Integer, nullable=True)
    target_weight = Column(Float, nullable=True)
    rest_seconds = Column(Integer, default=90)

    notes = Column(Text, nullable=True)

    # Relationships
    routine = relationship("Routine", back_populates="routine_exercises")
    exercise = relationship("Exercise")

    def __repr__(self):
        return f"<RoutineExercise(routine_id={self.routine_id}, exercise_id={self.exercise_id})>"