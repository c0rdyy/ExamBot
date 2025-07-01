from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_panel_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Все вопросы"), KeyboardButton(text="➕ Добавить вопрос")],
        [KeyboardButton(text="🗑 Удалить вопрос"), KeyboardButton(text="✏️ Редактировать вопрос")],
        [KeyboardButton(text="👤 Назначить админа")]
    ],
    resize_keyboard=True
)