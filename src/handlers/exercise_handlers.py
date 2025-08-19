import logging
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from src.services.exercise_service import list_exercises, find_exercises_by_name
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()
logger = logging.getLogger(__name__)

PAGE_SIZE = 5

#===============
# /exercises 
#===============

def format_exercise(ex):
    return f"🏋️ {ex.name}\n📂 Категория: {ex.category}\n💪 Мышца: {ex.primary_muscle}\n"

def get_exercise_page(session, page=0):
    exercises = list_exercises(session)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    chunk = exercises[start:end]

    text = "\n\n".join([format_exercise(ex) for ex in chunk]) or "Нет упражнений"
    
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


# ======================
# /search_exercise
#====================

class SearchExercise(StatesGroup):
    waiting_for_name = State()

@router.message(F.text == "/search_exercise")
async def start_search(message: Message, state: FSMContext):
    await state.set_state(SearchExercise.waiting_for_name)
    await message.answer("Введите название упражнения:")

@router.message(SearchExercise.waiting_for_name)
async def process_search(message: Message, state: FSMContext, session):
    query = message.text.strip()
    user_id = message.from_user.id

    if not query or len(query) < 2:
        logger.info(f"User {user_id} made invalid query: '{query}'")
        await message.answer("Некорректный запрос. Попробуйте ещё раз.")
        return

    results = find_exercises_by_name(session, query)
    if results:
        text = "\n".join([f"{ex.name} — {ex.primary_muscle}" for ex in results])
        logger.info(f"User {user_id} searched '{query}' → {len(results)} results")
    else:
        text = "Упражнение не найдено."
        logger.info(f"User {user_id} searched '{query}' → no results")

    await message.answer(text)
    await state.clear()

#==============
# /categories
# ==============
@router.message(F.text == "/categories")
async def show_categories(message: Message, session):
    exercises = list_exercises(session)
    categories = sorted(set(ex.category for ex in exercises if ex.category))

    if not categories:
        await message.answer("Категории не найдены.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=c)] for c in categories],
        resize_keyboard=True
    )
    await message.answer("Выберите категорию:", reply_markup=keyboard)

@router.message()
async def handle_category_choice(message: Message, session):
    category = message.text.strip()
    exercises = list_exercises(session)
    filtered = [ex for ex in exercises if ex.category == category]

    if filtered:
        text = "\n".join([f"{ex.name} — {ex.primary_muscle}" for ex in filtered])
    else:
        text = "В этой категории пока нет упражнений."

    await message.answer(text, reply_markup=None) 
