from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from src.services.exercise_service import list_exercises

router = Router()

PAGE_SIZE = 5

def get_exercise_page(session, page=0):
    exercises = list_exercises(session)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    chunk = exercises[start:end]

    text = "\n".join([f"{ex.id}. {ex.name} ({ex.category})" for ex in chunk]) or "Нет упражнений"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"ex_prev:{page}"),
            InlineKeyboardButton(text="➡️ Далее", callback_data=f"ex_next:{page}")
        ]
    ])
    return text, keyboard

@router.message(F.text == "/exercises")
async def show_exercises(message: Message, session):
    text, keyboard = get_exercise_page(session, page=0)
    await message.answer(text, reply_markup=keyboard)

