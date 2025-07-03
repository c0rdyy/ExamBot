from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def user_main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🧠 Начать тест")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🏆 Рейтинг")],
        [KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def admin_main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🧠 Начать тест")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🏆 Рейтинг")],
        [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="🛠 Админ-панель")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )