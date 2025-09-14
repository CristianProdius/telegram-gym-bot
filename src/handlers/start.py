import logging
from aiogram import Router, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters.callback_data import CallbackData

from src.services.user_service import UserService
from src.locales.translations import i18n
from src.database.connection import get_session

logger = logging.getLogger(__name__)

# Callback data for language selection
class LangCallback(CallbackData, prefix="lang"):
    code: str

def register_start_handlers(dp: Dispatcher):
    """Register start and help handlers"""
    router = Router()
    user_service = UserService()

    @router.message(CommandStart())
    async def cmd_start(message: Message):
        """Handle /start command"""
        logger.info(f"User {message.from_user.id} started the bot")

        async with get_session() as session:
            # Get or create user
            user = await user_service.get_or_create_user(
                session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code or 'en'
            )

            # If new user, ask for language preference
            if not user.language_code or user.language_code not in ['en', 'ru']:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🇬🇧 English", callback_data=LangCallback(code="en").pack()),
                        InlineKeyboardButton(text="🇷🇺 Русский", callback_data=LangCallback(code="ru").pack())
                    ]
                ])

                await message.answer(
                    "🌍 Please select your language / Пожалуйста, выберите язык:",
                    reply_markup=keyboard
                )
            else:
                # Set user language preference
                i18n.set_user_language(message.from_user.id, user.language_code)

                # Send welcome message
                welcome_text = i18n.get("welcome", message.from_user.id)
                await message.answer(welcome_text)

    @router.callback_query(LangCallback.filter())
    async def process_language_selection(callback: CallbackQuery, callback_data: LangCallback):
        """Process language selection"""
        user_id = callback.from_user.id
        lang_code = callback_data.code

        async with get_session() as session:
            user_service = UserService()
            await user_service.update_user_language(session, user_id, lang_code)

        # Set language in translation manager
        i18n.set_user_language(user_id, lang_code)

        # Send welcome message in selected language
        welcome_text = i18n.get("welcome", user_id)
        await callback.message.edit_text(welcome_text)

        # Send confirmation
        lang_changed = i18n.get("language_changed", user_id)
        await callback.answer(lang_changed)

    @router.message(Command("help"))
    async def cmd_help(message: Message):
        """Handle /help command"""
        logger.info(f"User {message.from_user.id} requested help")

        # Get help text in user's language
        help_text = i18n.get("help", message.from_user.id)
        await message.answer(help_text)

    @router.message(Command("language", "lang", "settings"))
    async def cmd_language(message: Message):
        """Handle language change command"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data=LangCallback(code="en").pack()),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data=LangCallback(code="ru").pack())
            ]
        ])

        text = "🌍 Select language / Выберите язык:"
        await message.answer(text, reply_markup=keyboard)

    dp.include_router(router)