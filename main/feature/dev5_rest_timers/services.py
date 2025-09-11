import asyncio
from datetime import datetime, time

class Timer:
    def __init__(self, duration_seconds: int):
        self.duration = duration_seconds
        self.start_time = None
        self.task = None

    def start(self):
        self.start_time = datetime.now()

    def remaining_seconds(self) -> int:
        if not self.start_time:
            return self.duration
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return max(0, self.duration - int(elapsed))

# Хранилища для таймеров
timers: dict[int, Timer] = {}
settings: dict[int, dict[str, int]] = {}

# Хранилища для планировщика
schedules: dict[int, list] = {}
user_states: dict[int, dict] = {}
day_map = {'Mo': 0, 'Tu': 1, 'We': 2, 'Th': 3, 'Fr': 4, 'Sa': 5, 'Su': 6}
day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_codes = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

async def reminder_loop(chat_id: int, weekday: int, train_time: time):
    while True:
        now = datetime.now()
        days_ahead = weekday - now.weekday()
        if days_ahead < 0:
            days_ahead += 7
        next_train_dt = now + timedelta(days=days_ahead)
        next_train_dt = next_train_dt.replace(hour=train_time.hour, minute=train_time.minute, second=0, microsecond=0)
        if next_train_dt <= now:
            next_train_dt += timedelta(days=7)
        next_reminder_dt = next_train_dt - timedelta(hours=1)
        if next_reminder_dt <= now:
            next_train_dt += timedelta(days=7)
            next_reminder_dt = next_train_dt - timedelta(hours=1)
        wait_seconds = (next_reminder_dt - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        try:
            from .handlers import bot  # Импортируем bot из main
            await bot.send_message(chat_id, "Training in one hour!")
        except:
            pass  # Ignore sending errors