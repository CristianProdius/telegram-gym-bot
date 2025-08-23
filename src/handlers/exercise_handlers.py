import logging
import aiohttp
from aiogram import Router, F, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from src.services.exercise_service import list_exercises, find_exercises_by_name
from src.services.wger_service import fetch_wger_exercises
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, constr, ValidationError

router = Router()
logger = logging.getLogger(__name__)
PAGE_SIZE = 5

#===============
# /start
#===============
@router.message(F.text == '/start')
async def start_command(message: Message):
    await message.answer('Привет! Я бот для тренировок. Используй команды:\n/exercises — список упражнений\n/search_exercise — поиск упражнения\n/categories — выбор категории\n/wger_exercises — упражнения из Wger API')

#===============
# /exercises
#===============
def format_exercise(ex):
    return f'🏋️ {ex.name}\n📂 Категория: {ex.category}\n💪 Мышца: {ex.primary_muscle}\n'

def get_exercise_page(session, page=0):
    exercises = list_exercises(session)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    chunk = exercises[start:end]
    text = '\n\n'.join([format_exercise(ex) for ex in chunk]) or 'Нет упражнений'
    prev_button = InlineKeyboardButton(text='⬅️ Назад', callback_data=f'ex_prev:{page-1}') if page > 0 else None
    next_button = InlineKeyboardButton(text='➡️ Далее', callback_data=f'ex_next:{page+1}') if end < len(exercises) else None
    buttons = [b for b in [prev_button, next_button] if b]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons] if buttons else [])
    return text, keyboard

@router.message(F.text == '/exercises')
async def show_exercises(message: Message, session: AsyncSession):
    text, keyboard = get_exercise_page(session, page=0)
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith('ex_'))
async def handle_pagination(callback: types.CallbackQuery, session: AsyncSession):
    page = int(callback.data.split(':')[1])
    text, keyboard = get_exercise_page(session, page)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

#=====================
# /search_exercise
#====================
class SearchExercise(StatesGroup):
    waiting_for_name = State()

class SearchQuery(BaseModel):
    query: constr(min_length=2, pattern=r'^[a-zA-Z\s]+$')

@router.message(F.text == '/search_exercise')
async def start_search(message: Message, state: FSMContext):
    await state.set_state(SearchExercise.waiting_for_name)
    await message.answer('Введите название упражнения (только буквы и пробелы, минимум 2 символа):')

@router.message(SearchExercise.waiting_for_name)
async def process_search(message: Message, state: FSMContext, session: AsyncSession):
    query = message.text.strip()
    user_id = message.from_user.id
    try:
        validated_query = SearchQuery(query=query)
        results = await find_exercises_by_name(session, validated_query.query)
        if results:
            text = '\n'.join([f'{ex.name} — {ex.primary_muscle}' for ex in results])
            logger.info(f'User {user_id} searched \'{query}\' → {len(results)} results')
        else:
            text = 'Упражнение не найдено.'
            logger.info(f'User {user_id} searched \'{query}\' → no results')
        await message.answer(text)
    except ValidationError as e:
        logger.info(f'User {user_id} provided invalid query: \'{query}\'')
        await message.answer('Некорректный запрос. Используйте только буквы и пробелы, минимум 2 символа.')
    await state.clear()

#==============
# /categories
#==============
class CategorySelection(StatesGroup):
    waiting_for_category = State()

async def get_categories(session: AsyncSession):
    exercises = await list_exercises(session)
    return sorted(set(ex.category for ex in exercises if ex.category))

@router.message(F.text == '/categories')
async def show_categories(message: Message, state: FSMContext, session: AsyncSession):
    categories = await get_categories(session)
    if not categories:
        await message.answer('Категории не найдены.')
        return
    await state.set_state(CategorySelection.waiting_for_category)
    await state.update_data(categories=categories)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=c)] for c in categories],
        resize_keyboard=True
    )
    await message.answer('Выберите категорию:', reply_markup=keyboard)

@router.message(CategorySelection.waiting_for_category)
async def handle_category_choice(message: Message, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    categories = user_data.get('categories', [])
    category = message.text.strip()
    if category not in categories:
        await message.answer('Пожалуйста, выберите категорию из предложенных.')
        return
    exercises = await list_exercises(session)
    filtered = [ex for ex in exercises if ex.category == category]
    if filtered:
        text = '\n'.join([f'{ex.name} — {ex.primary_muscle}' for ex in filtered])
    else:
        text = 'В этой категории пока нет упражнений.'
    await message.answer(text, reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True))
    await state.clear()

#==============
# /wger_exercises
#==============
@router.message(F.text == '/wger_exercises')
async def show_wger_exercises(message: Message):
    async with aiohttp.ClientSession() as session:
        exercises = await fetch_wger_exercises(session, limit=5)
        if exercises:
            text = '\n'.join([f'{ex["name"]} — {ex["category"]["name"]}' for ex in exercises])
        else:
            text = 'Не удалось загрузить упражнения из Wger API.'
        await message.answer(text)
