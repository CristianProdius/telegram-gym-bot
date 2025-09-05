import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
#Импорт внешних пакетов из requirements.txt

# (Даниил) Импорт моих скриптов.
# Добавляем папку feature в путь поиска модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'feature'))
# Теперь импортируем из пакета dev1_workout_tracking
from feature.dev1_workout_tracking.db import init_db
from feature.dev1_workout_tracking.workout_tracking import router as workout_router

# from dev2_module import router as dev2_router
# from dev3_module import router as dev3_router
# ... и так далее для dev4, dev5, dev6

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(TOKEN)
Dispatcher = Dispatcher()

# Роутер для основных команд из скрипта main.py
main_router = Router()
echo_router = Router()

# Включаем (include) все роутер в диспетчере
# Включение main роутера.
Dispatcher.include_router(main_router)

# Включение роутеров разработчиков.
Dispatcher.include_router(workout_router)

# Включение эхо роутера.
Dispatcher.include_router(echo_router)
# dp.include_router(dev3_router)
# ... и так далее

async def main():
    # Инициализируем базу данных
    init_db()
    # Запускаем поллинг
    await Dispatcher.start_polling(bot)

@main_router.message(CommandStart())
async def on_start(m: Message):
    await m.answer("Привет! Я помогу логировать тренировки.\nКоманды: /log, /today, /help")

@main_router.message(Command("help"))
async def on_help(m: Message):
    await m.answer("Примеры:\n/log BenchPress 3x10x50\n/today — показать сегодняшние записи")

# Эхо-хэндлер тоже можно оставить здесь или вынести в основной main.py
@echo_router.message(F.text)
async def echo(m: Message):
    await m.answer(f"Ты написал: {m.text}")

if __name__ == "__main__":
    asyncio.run(main())