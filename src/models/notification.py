from sqlalchemy import Column, Integer, String, Time, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.connection import Base

class TrainingNotification(Base):
    __tablename__ = "training_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weekday = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    training_time = Column(Time, nullable=False)
    reminder_minutes_before = Column(Integer, default=60, nullable=False)  # Minutes before training to send reminder
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="training_notifications")

    def __repr__(self):
        return f"<TrainingNotification(user_id={self.user_id}, weekday={self.weekday}, time={self.training_time}, reminder={self.reminder_minutes_before}min)>"