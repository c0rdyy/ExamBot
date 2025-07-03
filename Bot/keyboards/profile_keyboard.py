from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

edit_profile_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏ Изменить имя")],
        [KeyboardButton(text="🖼 Загрузить фото"), KeyboardButton(text="🗑 Удалить фото")],
        [KeyboardButton(text="🔙 Назад в меню")]
    ],
    resize_keyboard=True
)
