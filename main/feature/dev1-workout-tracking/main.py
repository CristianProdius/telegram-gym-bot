import asyncio, os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command


#Step 2
from db import SessionLocal, init_db
from models import Workout
from aiogram.filters import Command
import re
from datetime import datetime , timezone

#step 4
from sqlalchemy import select

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def on_start(m: Message):
    await m.answer("Привет! Я помогу логировать тренировки.\nКоманды: /log, /today, /help")

@router.message(Command("help"))
async def on_help(m: Message):
    await m.answer("Примеры:\n/log BenchPress 3x10x50\n/today — показать сегодняшние записи")

@router.message(Command("log"))
async def log_workout(m: Message):
    # ожидаем: /log BenchPress 3x10x50
    parts = m.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        return await m.answer("Формат: /log Exercise 3x10x50")

    exercise = parts[1]
    m2 = re.match(r"^(\d+)x(\d+)x(\d+)$", parts[2])
    if not m2:
        return await m.answer("Пример: /log BenchPress 3x10x50")

    sets, reps, weight = map(int, m2.groups())

    # Синхронная запись в SQLite (на MVP так можно)
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
        # берём записи за последние 24ч (упростим)
        q = select(Workout).where(Workout.user_id == m.from_user.id).order_by(Workout.created_at.desc()).limit(20)
        rows = session.execute(q).scalars().all()
        if not rows:
            return await m.answer("Сегодня записей нет.")
        lines = [f"{r.created_at:%H:%M} — {r.exercise} {r.sets}x{r.reps}x{r.weight} кг" for r in rows]
        await m.answer("Последние записи:\n" + "\n".join(lines))
    finally:
        session.close()

# Временно — эхо всего остального
@router.message(F.text)
async def echo(m: Message):
    await m.answer(f"Ты написал: {m.text}")

dp.include_router(router)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
