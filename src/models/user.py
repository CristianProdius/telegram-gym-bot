from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    language_code = Column(String, default="ru", nullable=False)

    # User preferences
    weight_unit = Column(String, default="kg", nullable=False)  # kg or lbs
    timezone = Column(String, default="UTC", nullable=False)
    notification_enabled = Column(Boolean, default=True, nullable=False)
    reminder_time = Column(String, default="09:00", nullable=True)

    # Relationships
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    routines = relationship("Routine", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("ProgressRecord", back_populates="user", cascade="all, delete-orphan")
    training_notifications = relationship("TrainingNotification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"