from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

help_back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main_menu")]
    ]
)
