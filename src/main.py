# src/main.py
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.handlers.exercise_handlers import router

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.exercise import Base
from src.data.seed_exercises import seed_exercises

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

engine = create_engine("sqlite:///exercises.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

if not session.query(Base.metadata.tables['exercises']).count():
    seed_exercises(session)

async def main():
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(router)

    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
