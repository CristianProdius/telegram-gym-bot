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
            "help": "📚 Available Commands:\n\n🏋️ Workouts:\n/log - Log a workout\n/today - Today's workouts\n/history - Workout history\n\n🥬 Nutrition:\n/nutrition - Track your nutrition\n\n⏱ Timers and notifications:\n/timer - Set rest timer\n/notification - Set a notification an hour before training\n\n📊 Progress:\n/stats - View statistics\n/progress - Progress charts\n/records - Personal records\n\n🎯 Routines:\n/routines - My routines\n/create_routine - Create routine\n\n👤 Profile:\n/profile - View profile\n/settings - Bot settings\n\n📤 Export:\n/export - Export data",

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

            # Reminder time selection
            "notification_select_reminder_time": "⏰ <b>Select Reminder Time</b>\n\nWhen do you want to be reminded before your training?\n\nChoose a preset time or enter a custom value:",
            "reminder_15_min": "⏱️ 15 minutes before",
            "reminder_30_min": "⏱️ 30 minutes before",
            "reminder_1_hour": "⏱️ 1 hour before",
            "reminder_2_hours": "⏱️ 2 hours before",
            "reminder_custom": "✏️ Custom time",
            
            # Custom reminder input
            "notification_enter_custom_reminder": "⏰ <b>Enter Custom Reminder Time</b>\n\nEnter how many minutes before training you want to be reminded:\n\n<i>Examples: 45, 90, 120</i>\n\n(Maximum: 1440 minutes = 24 hours)",
            "notification_invalid_reminder_format": "❌ Invalid format!\n\nPlease enter a number of minutes.\nExamples: 45, 90, 120",
            "notification_invalid_reminder_range": "❌ Invalid reminder time!\n\nPlease enter a value between 1 and 1440 minutes (1-24 hours).",
            
            # Reminder time formatting
            "reminder_format_minutes": "{minutes} min before",
            "reminder_format_hours": "{hours}h before",
            "reminder_format_hours_minutes": "{hours}h {minutes}min before",
            
            # Updated notification messages
            "notification_menu": "🔔 <b>Training Notifications</b>\n\nManage your training reminders. Set custom reminder times for each workout!\n\nChoose an action:",
            "notification_list": "📋 <b>Your Training Notifications</b>\n\n{notifications}\n\n💡 You'll receive reminders at your chosen times before each training session.",
            "notification_added": "✅ <b>Training Notification Added!</b>\n\n📅 Day: <b>{day}</b>\n🕐 Time: <b>{time}</b>\n⏰ Reminder: <b>{reminder}</b>\n\nYou'll be notified at the specified time! 🔔",
            "notification_updated": "✅ <b>Training Notification Updated!</b>\n\n📅 Day: <b>{day}</b>\n🕐 Time: <b>{time}</b>\n⏰ Reminder: <b>{reminder}</b>\n\nYour reminder has been rescheduled! 🔔",
            
            # Training reminders with custom times
            "training_reminder_minutes": "🏋️‍♂️ <b>Training Reminder</b>\n\nYour training starts in {minutes} minutes! Time to get ready! 💪",
            "training_reminder_hours": "🏋️‍♂️ <b>Training Reminder</b>\n\nYour training starts in {hours} hour(s)! Time to get ready! 💪",
            "training_reminder_hours_minutes": "🏋️‍♂️ <b>Training Reminder</b>\n\nYour training starts in {hours} hour(s) and {minutes} minutes! Time to get ready! 💪",

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

            # Nutrition main messages
            "nutrition_welcome": "🍎 <b>Welcome to Nutrition Tracker!</b>\n\nTrack your daily nutrition with comprehensive features:\n\n🔍 <b>Add Food</b> - Search and log meals\n📊 <b>Daily Summary</b> - See your progress\n🎯 <b>Set Goals</b> - Define nutrition targets\n📝 <b>View Meals</b> - Review logged foods\n\nChoose an option below to get started!",
            "nutrition_main_menu": "☰ Main Menu",
            "nutrition_add_food": "🔍 Add Food",
            "nutrition_daily_summary": "📊 Daily Summary",
            "nutrition_set_goals": "🎯 Set Goals",
            "nutrition_view_meals": "📝 View Meals",

            # Meal type selection
            "nutrition_select_meal_type": "🍽️ <b>Add Food to Meal</b>\n\nFirst, select which meal you're logging:",
            "meal_breakfast": "🥞 Breakfast",
            "meal_lunch": "🥗 Lunch",
            "meal_dinner": "🍽️ Dinner",
            "meal_snack": "🍎 Snack",

            # Food search
            "nutrition_enter_food_search": "🔍 <b>Adding food to {meal_type}</b>\n\nPlease enter the name of the food you want to search for:\n\n<i>Example: Chicken breast, Banana, Rice, etc.</i>",
            "nutrition_invalid_search": "Please provide a valid food name to search for.",
            "nutrition_searching": "🔍 Searching for foods...",
            "nutrition_no_results": "❌ No results found for '{query}'. Please try a different search term.",
            "nutrition_search_results": "🔍 <b>Search results for '{query}':</b>\n\nSelect a food to add to your meal:",

            # Food details
            "nutrition_getting_food_info": "⏳ Getting food information...",
            "nutrition_food_info_error": "❌ Sorry, I couldn't get information for this food.",
            "nutrition_food_details": "📊 <b>{name}</b>\n\n<b>Nutrition per 100g:</b>\n🔥 Calories: {calories:.1f} kcal\n🥩 Protein: {protein:.1f}g\n🍞 Carbs: {carbs:.1f}g\n🥑 Fat: {fat:.1f}g\n\n<b>Enter portion size in grams:</b>\n<i>Example: 150 (for 150 grams)</i>",
            "nutrition_invalid_portion": "Please enter a positive number for the portion size.",
            "nutrition_invalid_number": "Please enter a valid number.",
            "nutrition_food_not_found": "Food not found. Please try again.",

            # Meal logging
            "nutrition_meal_logged": "✅ <b>Food logged successfully!</b>\n\n{meal_type}\n🍽️ {food_name} ({portion}g)\n\n<b>Nutrition added:</b>\n🔥 Calories: {calories:.1f} kcal\n🥩 Protein: {protein:.1f}g\n🍞 Carbs: {carbs:.1f}g\n🥑 Fat: {fat:.1f}g",
            "nutrition_add_more": "➕ Add More Food",
            "nutrition_view_summary": "📊 View Daily Summary",

            # Daily summary
            "nutrition_daily_summary_full": "📊 <b>Daily Summary - {date}</b>\n\n<b>Today's Intake:</b>\n🔥 Calories: {calories:.1f} kcal\n🥩 Protein: {protein:.1f}g\n🍞 Carbs: {carbs:.1f}g\n🥑 Fat: {fat:.1f}g\n\n<b>Progress vs Goals:</b>\n🎯 Calories: {cal_percent:.1f}% ({calories:.1f}/{goal_calories:.1f})\n🎯 Protein: {protein_percent:.1f}% ({protein:.1f}/{goal_protein:.1f}g)\n🎯 Carbs: {carbs_percent:.1f}% ({carbs:.1f}/{goal_carbs:.1f}g)\n🎯 Fat: {fat_percent:.1f}% ({fat:.1f}/{goal_fat:.1f}g)",

            # Goals setting
            "nutrition_set_goals_start": "🎯 <b>Current Daily Goals:</b>\n\n🔥 Calories: {calories:.0f} kcal\n🥩 Protein: {protein:.0f}g\n🍞 Carbs: {carbs:.0f}g\n🥑 Fat: {fat:.0f}g\n\n<b>Enter your new daily calorie goal:</b>\n<i>Example: 2000</i>",
            "nutrition_invalid_calories": "Please enter a valid calorie goal between 1 and 10000.",
            "nutrition_invalid_protein": "Please enter a valid protein goal between 1 and 500g.",
            "nutrition_invalid_carbs": "Please enter a valid carbohydrate goal between 1 and 1000g.",
            "nutrition_invalid_fat": "Please enter a valid fat goal between 1 and 300g.",
            "nutrition_calories_set": "✅ Calorie goal set to {calories:.0f} kcal\n\n<b>Now enter your daily protein goal (in grams):</b>\n<i>Example: 150</i>",
            "nutrition_protein_set": "✅ Protein goal set to {protein:.0f}g\n\n<b>Now enter your daily carbohydrate goal (in grams):</b>\n<i>Example: 250</i>",
            "nutrition_carbs_set": "✅ Carbohydrate goal set to {carbs:.0f}g\n\n<b>Finally, enter your daily fat goal (in grams):</b>\n<i>Example: 70</i>",
            "nutrition_goals_saved": "🎯 <b>Goals Set Successfully!</b>\n\nYour daily nutrition targets:\n🔥 Calories: {calories:.0f} kcal\n🥩 Protein: {protein:.0f}g\n🍞 Carbs: {carbs:.0f}g\n🥑 Fat: {fat:.0f}g\n\nYou can now track your progress against these goals!",

            # Meal viewing
            "nutrition_no_meals_today": "📝 <b>Today's Meals</b>\n\nNo meals logged today yet!\n\nStart by adding some food to track your nutrition.",
            "nutrition_todays_meals": "📝 Today's Meals - {date}",

            # Error messages
            "error_user_not_found": "❌ User not found. Please use /start first.",
        },

        "ru": {
            # Welcome and help messages
            "welcome": "👋 Добро пожаловать в Gym Bot! Я ваш персональный помощник для тренировок.\n\nЯ помогу вам:\n• 📝 Вести дневник тренировок\n• ⏱ Устанавливать таймеры отдыха\n• 📊 Анализировать прогресс\n• 💪 Достигать целей\n\nИспользуйте /help для просмотра команд!",
            "help": "📚 Доступные команды:\n\n🏋️ Тренировки:\n/log - Записать тренировку\n/today - Сегодняшние тренировки\n/history - История тренировок\n\n🥬 Питание:\n/nutrition - Отслеживать свое питание\n\n⏱ Таймеры и уведомления:\n/timer - Установить таймер\n/notification - Поставить уведомление за час до тренировки\n\n📊 Прогресс:\n/stats - Статистика\n/progress - Графики прогресса\n/records - Личные рекорды\n\n🎯 Программы:\n/routines - Мои программы\n/create_routine - Создать программу\n\n👤 Профиль:\n/profile - Мой профиль\n/settings - Настройки\n\n📤 Экспорт:\n/export - Экспорт данных",

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

            # Reminder time selection
            "notification_select_reminder_time": "⏰ <b>Выбор времени напоминания</b>\n\nКогда вы хотите получить напоминание перед тренировкой?\n\nВыберите готовое время или введите своё значение:",
            "reminder_15_min": "⏱️ За 15 минут",
            "reminder_30_min": "⏱️ За 30 минут",
            "reminder_1_hour": "⏱️ За 1 час",
            "reminder_2_hours": "⏱️ За 2 часа",
            "reminder_custom": "✏️ Своё время",
    
            # Custom reminder input
            "notification_enter_custom_reminder": "⏰ <b>Введите время напоминания</b>\n\nВведите, за сколько минут до тренировки вы хотите получить напоминание:\n\n<i>Примеры: 45, 90, 120</i>\n\n(Максимум: 1440 минут = 24 часа)",
            "notification_invalid_reminder_format": "❌ Неверный формат!\n\nПожалуйста, введите количество минут.\nПримеры: 45, 90, 120",
            "notification_invalid_reminder_range": "❌ Неверное время напоминания!\n\nПожалуйста, введите значение от 1 до 1440 минут (1-24 часа).",
            
            # Reminder time formatting
            "reminder_format_minutes": "за {minutes} мин",
            "reminder_format_hours": "за {hours}ч",
            "reminder_format_hours_minutes": "за {hours}ч {minutes}мин",
            
            # Updated notification messages
            "notification_menu": "🔔 <b>Уведомления о тренировках</b>\n\nУправляйте напоминаниями о тренировках. Установите своё время напоминания для каждой тренировки!\n\nВыберите действие:",
            "notification_list": "📋 <b>Ваши уведомления о тренировках</b>\n\n{notifications}\n\n💡 Вы будете получать напоминания в выбранное вами время перед каждой тренировкой.",
            "notification_added": "✅ <b>Уведомление о тренировке добавлено!</b>\n\n📅 День: <b>{day}</b>\n🕐 Время: <b>{time}</b>\n⏰ Напоминание: <b>{reminder}</b>\n\nВы получите уведомление в указанное время! 🔔",
            "notification_updated": "✅ <b>Уведомление о тренировке обновлено!</b>\n\n📅 День: <b>{day}</b>\n🕐 Время: <b>{time}</b>\n⏰ Напоминание: <b>{reminder}</b>\n\nВаше напоминание перенесено! 🔔",
            
            # Training reminders with custom times
            "training_reminder_minutes": "🏋️‍♂️ <b>Напоминание о тренировке</b>\n\nВаша тренировка начнётся через {minutes} минут! Время готовиться! 💪",
            "training_reminder_hours": "🏋️‍♂️ <b>Напоминание о тренировке</b>\n\nВаша тренировка начнётся через {hours} час(а/ов)! Время готовиться! 💪",
            "training_reminder_hours_minutes": "🏋️‍♂️ <b>Напоминание о тренировке</b>\n\nВаша тренировка начнётся через {hours} час(а/ов) и {minutes} минут! Время готовиться! 💪",
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

            # Nutrition main messages
            "nutrition_welcome": "🍎 <b>Добро пожаловать в Трекер Питания!</b>\n\nОтслеживайте свое ежедневное питание с помощью комплексных функций:\n\n🔍 <b>Добавить еду</b> - Поиск и запись приемов пищи\n📊 <b>Дневная сводка</b> - Посмотрите свой прогресс\n🎯 <b>Установить цели</b> - Определите цели по питанию\n📝 <b>Просмотр приемов пищи</b> - Просмотрите записанную еду\n\nВыберите опцию ниже, чтобы начать!",
            "nutrition_main_menu": "☰ Главное меню",
            "nutrition_add_food": "🔍 Добавить еду",
            "nutrition_daily_summary": "📊 Дневная сводка",
            "nutrition_set_goals": "🎯 Установить цели",
            "nutrition_view_meals": "📝 Просмотр приемов пищи",

            # Meal type selection
            "nutrition_select_meal_type": "🍽️ <b>Добавить еду к приему пищи</b>\n\nСначала выберите, какой прием пищи вы записываете:",
            "meal_breakfast": "🥞 Завтрак",
            "meal_lunch": "🥗 Обед",
            "meal_dinner": "🍽️ Ужин",
            "meal_snack": "🍎 Перекус",

            # Food search
            "nutrition_enter_food_search": "🔍 <b>Добавление еды к {meal_type}</b>\n\nПожалуйста, введите название еды, которую хотите найти:\n\n<i>Пример: Куриная грудка, Банан, Рис и т.д.</i>",
            "nutrition_invalid_search": "Пожалуйста, укажите действительное название еды для поиска.",
            "nutrition_searching": "🔍 Поиск продуктов...",
            "nutrition_no_results": "❌ Не найдено результатов для '{query}'. Попробуйте другой поисковый запрос.",
            "nutrition_search_results": "🔍 <b>Результаты поиска для '{query}':</b>\n\nВыберите еду, чтобы добавить к приему пищи:",

            # Food details
            "nutrition_getting_food_info": "⏳ Получение информации о еде...",
            "nutrition_food_info_error": "❌ Извините, не удалось получить информацию об этом продукте.",
            "nutrition_food_details": "📊 <b>{name}</b>\n\n<b>Питательность на 100г:</b>\n🔥 Калории: {calories:.1f} ккал\n🥩 Белок: {protein:.1f}г\n🍞 Углеводы: {carbs:.1f}г\n🥑 Жир: {fat:.1f}г\n\n<b>Введите размер порции в граммах:</b>\n<i>Пример: 150 (для 150 граммов)</i>",
            "nutrition_invalid_portion": "Пожалуйста, введите положительное число для размера порции.",
            "nutrition_invalid_number": "Пожалуйста, введите действительное число.",
            "nutrition_food_not_found": "Еда не найдена. Попробуйте снова.",

            # Meal logging
            "nutrition_meal_logged": "✅ <b>Еда успешно записана!</b>\n\n{meal_type}\n🍽️ {food_name} ({portion}г)\n\n<b>Добавлено питательных веществ:</b>\n🔥 Калории: {calories:.1f} ккал\n🥩 Белок: {protein:.1f}г\n🍞 Углеводы: {carbs:.1f}г\n🥑 Жир: {fat:.1f}г",
            "nutrition_add_more": "➕ Добавить еще еду",
            "nutrition_view_summary": "📊 Посмотреть дневную сводку",

            # Daily summary
            "nutrition_daily_summary_full": "📊 <b>Дневная сводка - {date}</b>\n\n<b>Сегодняшнее потребление:</b>\n🔥 Калории: {calories:.1f} ккал\n🥩 Белок: {protein:.1f}г\n🍞 Углеводы: {carbs:.1f}г\n🥑 Жир: {fat:.1f}г\n\n<b>Прогресс к целям:</b>\n🎯 Калории: {cal_percent:.1f}% ({calories:.1f}/{goal_calories:.1f})\n🎯 Белок: {protein_percent:.1f}% ({protein:.1f}/{goal_protein:.1f}г)\n🎯 Углеводы: {carbs_percent:.1f}% ({carbs:.1f}/{goal_carbs:.1f}г)\n🎯 Жир: {fat_percent:.1f}% ({fat:.1f}/{goal_fat:.1f}г)",

            # Goals setting
            "nutrition_set_goals_start": "🎯 <b>Текущие ежедневные цели:</b>\n\n🔥 Калории: {calories:.0f} ккал\n🥩 Белок: {protein:.0f}г\n🍞 Углеводы: {carbs:.0f}г\n🥑 Жир: {fat:.0f}г\n\n<b>Введите вашу новую ежедневную цель по калориям:</b>\n<i>Пример: 2000</i>",
            "nutrition_invalid_calories": "Пожалуйста, введите действительную цель по калориям между 1 и 10000.",
            "nutrition_invalid_protein": "Пожалуйста, введите действительную цель по белку между 1 и 500г.",
            "nutrition_invalid_carbs": "Пожалуйста, введите действительную цель по углеводам между 1 и 1000г.",
            "nutrition_invalid_fat": "Пожалуйста, введите действительную цель по жиру между 1 и 300г.",
            "nutrition_calories_set": "✅ Цель по калориям установлена на {calories:.0f} ккал\n\n<b>Теперь введите вашу ежедневную цель по белку (в граммах):</b>\n<i>Пример: 150</i>",
            "nutrition_protein_set": "✅ Цель по белку установлена на {protein:.0f}г\n\n<b>Теперь введите вашу ежедневную цель по углеводам (в граммах):</b>\n<i>Пример: 250</i>",
            "nutrition_carbs_set": "✅ Цель по углеводам установлена на {carbs:.0f}г\n\n<b>Наконец, введите вашу ежедневную цель по жиру (в граммах):</b>\n<i>Пример: 70</i>",
            "nutrition_goals_saved": "🎯 <b>Цели успешно установлены!</b>\n\nВаши ежедневные цели по питанию:\n🔥 Калории: {calories:.0f} ккал\n🥩 Белок: {protein:.0f}г\n🍞 Углеводы: {carbs:.0f}г\n🥑 Жир: {fat:.0f}г\n\nТеперь вы можете отслеживать свой прогресс по этим целям!",

            # Meal viewing
            "nutrition_no_meals_today": "📝 <b>Сегодняшние приемы пищи</b>\n\nСегодня еще не записано приемов пищи!\n\nНачните с добавления еды для отслеживания питания.",
            "nutrition_todays_meals": "📝 Сегодняшние приемы пищи - {date}",

            # Error messages
            "error_user_not_found": "❌ Пользователь не найден. Пожалуйста, сначала используйте /start.",
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