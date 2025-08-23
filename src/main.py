import asyncio
import logging
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.handlers.exercise_handlers import router
from environs import Env
from src.data.seed_exercises import seed_exercises

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

# Загрузка переменных окружения
env = Env()
env.read_env()
BOT_TOKEN = env.str('TELEGRAM_TOKEN')

# Настройка базы данных
engine = create_async_engine('sqlite+aiosqlite:///database.db', echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Middleware для передачи сессии
class DatabaseSessionMiddleware:
    def __init__(self, session_pool):
        self.session_pool = session_pool

    async def __call__(self, handler, event, data):
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.update.outer_middleware(DatabaseSessionMiddleware(async_session))
dp.include_router(router)

# Запуск бота
async def main():
    # Инициализация базы данных
    async with async_session() as session:
        async with session.begin():
            await seed_exercises(session)
    await dp.start_polling(bot, polling_timeout=15)

if __name__ == '__main__':
    asyncio.run(main())
