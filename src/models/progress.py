from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.connection import Base

class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Performance metrics
    one_rep_max = Column(Float, nullable=True)
    total_volume = Column(Float, nullable=True)
    max_weight = Column(Float, nullable=True)
    max_reps = Column(Integer, nullable=True)

    # Body measurements
    body_weight = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    measurements = Column(JSON, nullable=True)  # Store various body measurements

    # Photo references
    photo_url = Column(String, nullable=True)

    notes = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="progress_records")
    exercise = relationship("Exercise")

    def __repr__(self):
        return f"<ProgressRecord(user_id={self.user_id}, date={self.date})>"

class PersonalRecord(Base):
    __tablename__ = "personal_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    record_type = Column(String, nullable=False)  # "1RM", "MAX_REPS", "MAX_VOLUME", etc.
    value = Column(Float, nullable=False)
    date_achieved = Column(DateTime, default=datetime.utcnow, nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=True)

    # Relationships
    user = relationship("User")
    exercise = relationship("Exercise")
    workout = relationship("Workout")

    def __repr__(self):
        return f"<PersonalRecord(user_id={self.user_id}, exercise_id={self.exercise_id}, type={self.record_type})>"