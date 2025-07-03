from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

test_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Лёгкий", callback_data="difficulty_easy")],
        [InlineKeyboardButton(text="Средний", callback_data="difficulty_medium")],
        [InlineKeyboardButton(text="Сложный", callback_data="difficulty_hard")]
    ])

def build_question_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=opt, callback_data=f"answer_{i}")]
            for i, opt in enumerate(options)
        ]
    )

def build_number_keyboard(option_count: int) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=str(i+1), callback_data=f"answer_{i}")
        for i in range(option_count)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])