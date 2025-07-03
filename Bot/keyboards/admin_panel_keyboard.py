from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# admin_panel_main_menu = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text="📋 Все вопросы"), KeyboardButton(text="➕ Добавить вопрос")],
#         [KeyboardButton(text="🗑 Удалить вопрос"), KeyboardButton(text="✏️ Редактировать вопрос")],
#         [KeyboardButton(text="👤 Назначить админа")]
#     ],
#     resize_keyboard=True
# )

admin_panel_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Все вопросы", callback_data="all_questions")],
    [InlineKeyboardButton(text="➕ Добавить вопрос", callback_data="add_question"), 
    InlineKeyboardButton(text="🗑 Удалить вопрос", callback_data="delete_question")],
    [InlineKeyboardButton(text="✏️ Редактировать вопрос", callback_data="edit_question")],
    [InlineKeyboardButton(text="👤 Назначить админа", callback_data="create_admin")]
    ])
