from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime

class Base(DeclarativeBase):
    pass

class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)              # telegram_id
    exercise: Mapped[str] = mapped_column(String(100), index=True)
    sets: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int] = mapped_column(Integer)
    weight: Mapped[int] = mapped_column(Integer)                           # кг
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)