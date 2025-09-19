"""Translation management system for the gym bot"""

from typing import Dict, Optional

class Translations:
    """Container for all bot translations"""

    # Language codes
    ENGLISH = "en"
    RUSSIAN = "ru"

    # Default language
    DEFAULT_LANG = ENGLISH

    # Translation dictionaries
    MESSAGES: Dict[str, Dict[str, str]] = {
        "en": {
            # Welcome and help messages
            "welcome": "👋 Welcome to Gym Bot! I'm your personal workout assistant.\n\nI can help you:\n• 📝 Track workouts\n• ⏱ Set rest timers\n• 📊 Analyze progress\n• 💪 Achieve your goals\n\nUse /help to see all commands!",
            "help": "📚 Available Commands:\n\n🏋️ Workouts:\n/log - Log a workout\n/today - Today's workouts\n/history - Workout history\n\n⏱ Timers and notifications:\n/timer - Set rest timer\n/notification - Set a notification an hour before training\n\n📊 Progress:\n/stats - View statistics\n/progress - Progress charts\n/records - Personal records\n\n🎯 Routines:\n/routines - My routines\n/create_routine - Create routine\n\n👤 Profile:\n/profile - View profile\n/settings - Bot settings\n\n📤 Export:\n/export - Export data",

            # Workout messages
            "select_exercise": "Select an exercise or type to search:",
            "enter_sets": "How many sets did you complete?",
            "enter_reps": "Enter reps for set {set_number}:",
            "enter_weight": "Enter weight (kg) for set {set_number}:",
            "workout_saved": "✅ Workout saved successfully!",
            "no_workouts_today": "📅 No workouts logged today",
            "workout_history": "📊 Workout History (last {days} days):",

            # Timer messages
            "timer_config": "⏱ Configure your rest timer:",
            "timer_started": "⏳ Timer started for {seconds} seconds!",
            "timer_completed": "✅ Rest time complete! Ready for the next set?",
            "timer_stopped": "⏹ Timer stopped",

            # Progress messages
            "stats_overview": "📊 Your Statistics:\n\nTotal Workouts: {total_workouts}\nThis Week: {week_workouts}\nTotal Volume: {total_volume} kg\nFavorite Exercise: {favorite}",
            "personal_records": "🏆 Personal Records:\n\n{records}",
            "no_records": "No personal records yet. Keep training!",

            # Routine messages
            "routines_list": "🎯 Your Routines:\n\n{routines}",
            "no_routines": "You haven't created any routines yet.\nUse /create_routine to start!",
            "routine_created": "✅ Routine '{name}' created successfully!",

            # Settings messages
            "settings": "⚙️ Settings:\n\nLanguage: {language}\nWeight Unit: {unit}\nTimezone: {timezone}",
            "language_changed": "✅ Language changed to English",

            # Error messages
            "error_generic": "❌ An error occurred. Please try again.",
            "error_invalid_input": "❌ Invalid input. Please check and try again.",
            "error_not_found": "❌ Not found. Please try again.",

            # Button labels
            "btn_add_hour": "➕ Hour",
            "btn_add_minute": "➕ Minute",
            "btn_add_second": "➕ Second",
            "btn_sub_hour": "➖ Hour",
            "btn_sub_minute": "➖ Minute",
            "btn_sub_second": "➖ Second",
            "btn_start": "Start ✅",
            "btn_stop": "Stop ⛔",
            "btn_back": "⬅️ Back",
            "btn_cancel": "❌ Cancel",
            "btn_finish": "✅ Finish",

            # Notification messages
            "notification_menu": "🔔 <b>Training Notifications</b>\n\nManage your training reminders. Get notified 1 hour before your scheduled workouts!\n\nChoose an action:",
            "notification_add": "📅 <b>Add Training Notification</b>\n\nChoose the day of the week for your training:",
            "notification_list_empty": "📭 <b>No Training Notifications</b>\n\nYou haven't set up any training reminders yet.\nUse 'Add Training' to create your first notification!",
            "notification_list": "📋 <b>Your Training Notifications</b>\n\n{notifications}\n\n💡 You'll receive reminders 1 hour before each training session.",
            "notification_replace_empty": "📭 <b>No Training Notifications</b>\n\nYou don't have any training notifications to replace.\nUse 'Add Training' to create your first notification!",
            "notification_replace": "✏️ <b>Replace Training Notification</b>\n\nSelect the notification you want to replace:",
            "notification_max_limit": "⚠️ <b>Maximum Limit Reached</b>\n\nYou already have 5 training notifications:\n\n{notifications}\n\nUse 'Replace Training' to modify existing ones.",
            "notification_set_time": "🕒 <b>Set Training Time</b>\n\nSelected day: <b>{day}</b>\n\nPlease enter the training time in HH:MM format (24-hour):\n\nExamples: 09:30, 18:00, 20:15",
            "notification_set_new_time": "🕒 <b>Set New Training Time</b>\n\nSelected day: <b>{day}</b>\n\nPlease enter the new training time in HH:MM format (24-hour):\n\nExamples: 09:30, 18:00, 20:15",
            "notification_invalid_time_format": "❌ Invalid time format!\n\nPlease enter time in HH:MM format (24-hour).\nExamples: 09:30, 18:00, 20:15",
            "notification_invalid_time_range": "❌ Invalid time!\n\nPlease enter a valid time between 00:00 and 23:59.",
            "notification_added": "✅ <b>Training Notification Added!</b>\n\n📅 Day: <b>{day}</b>\n🕒 Time: <b>{time}</b>\n\nYou'll receive a reminder 1 hour before your training! 🔔",
            "notification_updated": "✅ <b>Training Notification Updated!</b>\n\n📅 Day: <b>{day}</b>\n🕒 Time: <b>{time}</b>\n\nYour reminder has been rescheduled! 🔔",
            "training_reminder": "🏋️‍♂️ <b>Training Reminder</b>\n\nYour training starts in 1 hour! Time to get ready! 💪",

            # Day names
            "day_monday": "Monday",
            "day_tuesday": "Tuesday", 
            "day_wednesday": "Wednesday",
            "day_thursday": "Thursday",
            "day_friday": "Friday",
            "day_saturday": "Saturday",
            "day_sunday": "Sunday",

            # Notification button labels
            "btn_add_training": "➕ Add Training",
            "btn_view_list": "📋 View List",
            "btn_replace_training": "✏️ Replace Training",
        },

        "ru": {
            # Welcome and help messages
            "welcome": "👋 Добро пожаловать в Gym Bot! Я ваш персональный помощник для тренировок.\n\nЯ помогу вам:\n• 📝 Вести дневник тренировок\n• ⏱ Устанавливать таймеры отдыха\n• 📊 Анализировать прогресс\n• 💪 Достигать целей\n\nИспользуйте /help для просмотра команд!",
            "help": "📚 Доступные команды:\n\n🏋️ Тренировки:\n/log - Записать тренировку\n/today - Сегодняшние тренировки\n/history - История тренировок\n\n⏱ Таймеры и уведомления:\n/timer - Установить таймер\n\n/notification - Поставить уведомление за час до тренировки\n📊 Прогресс:\n/stats - Статистика\n/progress - Графики прогресса\n/records - Личные рекорды\n\n🎯 Программы:\n/routines - Мои программы\n/create_routine - Создать программу\n\n👤 Профиль:\n/profile - Мой профиль\n/settings - Настройки\n\n📤 Экспорт:\n/export - Экспорт данных",

            # Workout messages
            "select_exercise": "Выберите упражнение или введите для поиска:",
            "enter_sets": "Сколько подходов вы выполнили?",
            "enter_reps": "Введите количество повторений для подхода {set_number}:",
            "enter_weight": "Введите вес (кг) для подхода {set_number}:",
            "workout_saved": "✅ Тренировка сохранена!",
            "no_workouts_today": "📅 Сегодня тренировок не было",
            "workout_history": "📊 История тренировок (последние {days} дней):",

            # Timer messages
            "timer_config": "⏱ Настройте таймер отдыха:",
            "timer_started": "⏳ Таймер запущен на {seconds} секунд!",
            "timer_completed": "✅ Время отдыха закончилось! Готовы к следующему подходу?",
            "timer_stopped": "⏹ Таймер остановлен",

            # Progress messages
            "stats_overview": "📊 Ваша статистика:\n\nВсего тренировок: {total_workouts}\nНа этой неделе: {week_workouts}\nОбщий объём: {total_volume} кг\nЛюбимое упражнение: {favorite}",
            "personal_records": "🏆 Личные рекорды:\n\n{records}",
            "no_records": "Личных рекордов пока нет. Продолжайте тренироваться!",

            # Routine messages
            "routines_list": "🎯 Ваши программы:\n\n{routines}",
            "no_routines": "У вас пока нет программ тренировок.\nИспользуйте /create_routine для создания!",
            "routine_created": "✅ Программа '{name}' создана успешно!",

            # Settings messages
            "settings": "⚙️ Настройки:\n\nЯзык: {language}\nЕдиницы веса: {unit}\nЧасовой пояс: {timezone}",
            "language_changed": "✅ Язык изменён на русский",

            # Error messages
            "error_generic": "❌ Произошла ошибка. Попробуйте снова.",
            "error_invalid_input": "❌ Неверный ввод. Проверьте и попробуйте снова.",
            "error_not_found": "❌ Не найдено. Попробуйте снова.",

            # Button labels
            "btn_add_hour": "➕ Час",
            "btn_add_minute": "➕ Минута",
            "btn_add_second": "➕ Секунда",
            "btn_sub_hour": "➖ Час",
            "btn_sub_minute": "➖ Минута",
            "btn_sub_second": "➖ Секунда",
            "btn_start": "Старт ✅",
            "btn_stop": "Стоп ⛔",
            "btn_back": "⬅️ Назад",
            "btn_cancel": "❌ Отмена",
            "btn_finish": "✅ Завершить",

            # Notification messages
            "notification_menu": "🔔 <b>Уведомления о тренировках</b>\n\nУправляйте напоминаниями о тренировках. Получайте уведомления за 1 час до запланированных тренировок!\n\nВыберите действие:",
            "notification_add": "📅 <b>Добавить уведомление о тренировке</b>\n\nВыберите день недели для тренировки:",
            "notification_list_empty": "📭 <b>Нет уведомлений о тренировках</b>\n\nВы ещё не настроили напоминания о тренировках.\nИспользуйте 'Добавить тренировку' для создания первого уведомления!",
            "notification_list": "📋 <b>Ваши уведомления о тренировках</b>\n\n{notifications}\n\n💡 Вы будете получать напоминания за 1 час до каждой тренировки.",
            "notification_replace_empty": "📭 <b>Нет уведомлений о тренировках</b>\n\nУ вас нет уведомлений о тренировках для замены.\nИспользуйте 'Добавить тренировку' для создания первого уведомления!",
            "notification_replace": "✏️ <b>Заменить уведомление о тренировке</b>\n\nВыберите уведомление, которое хотите заменить:",
            "notification_max_limit": "⚠️ <b>Достигнут максимальный лимит</b>\n\nУ вас уже есть 5 уведомлений о тренировках:\n\n{notifications}\n\nИспользуйте 'Заменить тренировку' для изменения существующих.",
            "notification_set_time": "🕒 <b>Установить время тренировки</b>\n\nВыбранный день: <b>{day}</b>\n\nВведите время тренировки в формате ЧЧ:ММ (24-часовой):\n\nПримеры: 09:30, 18:00, 20:15",
            "notification_set_new_time": "🕒 <b>Установить новое время тренировки</b>\n\nВыбранный день: <b>{day}</b>\n\nВведите новое время тренировки в формате ЧЧ:ММ (24-часовой):\n\nПримеры: 09:30, 18:00, 20:15",
            "notification_invalid_time_format": "❌ Неверный формат времени!\n\nВведите время в формате ЧЧ:ММ (24-часовой).\nПримеры: 09:30, 18:00, 20:15",
            "notification_invalid_time_range": "❌ Неверное время!\n\nВведите корректное время между 00:00 и 23:59.",
            "notification_added": "✅ <b>Уведомление о тренировке добавлено!</b>\n\n📅 День: <b>{day}</b>\n🕒 Время: <b>{time}</b>\n\nВы получите напоминание за 1 час до тренировки! 🔔",
            "notification_updated": "✅ <b>Уведомление о тренировке обновлено!</b>\n\n📅 День: <b>{day}</b>\n🕒 Время: <b>{time}</b>\n\nВаше напоминание перенесено! 🔔",
            "training_reminder": "🏋️‍♂️ <b>Напоминание о тренировке</b>\n\nВаша тренировка начнётся через 1 час! Время готовиться! 💪",

            # Day names
            "day_monday": "Понедельник",
            "day_tuesday": "Вторник",
            "day_wednesday": "Среда", 
            "day_thursday": "Четверг",
            "day_friday": "Пятница",
            "day_saturday": "Суббота",
            "day_sunday": "Воскресенье",

            # Notification button labels
            "btn_add_training": "➕ Добавить тренировку",
            "btn_view_list": "📋 Список",
            "btn_replace_training": "✏️ Заменить тренировку",
        }
    }

class TranslationManager:
    """Manager for handling translations"""

    def __init__(self):
        self.translations = Translations()
        self.user_languages: Dict[int, str] = {}

    def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language"""
        return self.user_languages.get(user_id, Translations.DEFAULT_LANG)

    def set_user_language(self, user_id: int, language: str):
        """Set user's preferred language"""
        if language in Translations.MESSAGES:
            self.user_languages[user_id] = language

    def get(self, key: str, user_id: int, **kwargs) -> str:
        """Get translated message for user"""
        lang = self.get_user_language(user_id)
        messages = Translations.MESSAGES.get(lang, Translations.MESSAGES[Translations.DEFAULT_LANG])
        message = messages.get(key, f"Missing translation: {key}")

        # Format message with provided kwargs
        if kwargs:
            try:
                message = message.format(**kwargs)
            except KeyError:
                pass

        return message

    def get_button(self, key: str, user_id: int) -> str:
        """Get translated button label"""
        return self.get(f"btn_{key}", user_id)

# Global translation manager instance
i18n = TranslationManager()