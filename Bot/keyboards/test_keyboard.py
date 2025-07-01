from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

test_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Лёгкий", callback_data="difficulty_easy")],
        [InlineKeyboardButton(text="Средний", callback_data="difficulty_medium")],
        [InlineKeyboardButton(text="Сложный", callback_data="difficulty_hard")]
    ])