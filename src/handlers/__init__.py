from aiogram import Dispatcher

from .start import register_start_handlers
from .workout import register_workout_handlers
from .timer import register_timer_handlers
from .stats import register_stats_handlers

def register_all_handlers(dp: Dispatcher):
    """Register all bot handlers"""
    register_start_handlers(dp)
    register_workout_handlers(dp)
    register_timer_handlers(dp)
    register_stats_handlers(dp)