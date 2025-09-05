# workout_tracking.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from .db import SessionLocal
from .models import Workout
import re
from datetime import datetime, timezone
from sqlalchemy import select

# Создаем свой собственный роутер для этого модуля
router = Router()

# Регистрируем хэндлеры на этом роутере

@router.message(Command("log"))
async def log_workout(m: Message):
    # ... (весь код функции остается без изменений)
    parts = m.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        return await m.answer("Формат: /log Exercise 3x10x50")

    exercise = parts[1]
    m2 = re.match(r"^(\d+)x(\d+)x(\d+)$", parts[2])
    if not m2:
        return await m.answer("Пример: /log BenchPress 3x10x50")

    sets, reps, weight = map(int, m2.groups())

    session = SessionLocal()
    try:
        w = Workout(
            user_id=m.from_user.id,
            exercise=exercise,
            sets=sets,
            reps=reps,
            weight=weight,
            created_at=datetime.now(timezone.utc),
        )
        session.add(w)
        session.commit()
        await m.answer(f"Записал: {exercise} — {sets}x{reps}x{weight} кг ✅")
    finally:
        session.close()

@router.message(Command("today"))
async def today(m: Message):
    session = SessionLocal()
    try:
        q = select(Workout).where(Workout.user_id == m.from_user.id).order_by(Workout.created_at.desc()).limit(20)
        rows = session.execute(q).scalars().all()
        if not rows:
            return await m.answer("Сегодня записей нет.")
        lines = [f"{r.created_at:%H:%M} — {r.exercise} {r.sets}x{r.reps}x{r.weight} кг" for r in rows]
        await m.answer("Последние записи:\n" + "\n".join(lines))
    finally:
        session.close()

# Функция для получения роутера из этого модуля (опционально, но удобно)
def get_router():
    return router