from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_panel_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Все вопросы", callback_data="all_questions"),
    InlineKeyboardButton(text="✏️ Редактировать вопрос", callback_data="edit_question")],
    [InlineKeyboardButton(text="➕ Добавить вопрос", callback_data="add_question"), 
    InlineKeyboardButton(text="🗑 Удалить вопрос", callback_data="delete_question")],
    [InlineKeyboardButton(text="👤 Назначить админа", callback_data="create_admin")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main_menu")]
    ])

admin_panel_back_to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main_menu")]
])

admin_panel_cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отменить действие", callback_data="cancel")]
])