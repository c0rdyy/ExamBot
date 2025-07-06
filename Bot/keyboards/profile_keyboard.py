from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать профиль", callback_data="edit_profile")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main_menu")]
])

profile_editting_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Изменить фото", callback_data="edit_photo")],
        [InlineKeyboardButton(text="📝 Изменить имя", callback_data="edit_name")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_profile_view")]
    ])

back_to_profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_profile_view")]])

choose_action_for_profile_photo = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Загрузить новое", callback_data="upload_photo")],
        [InlineKeyboardButton(text="🗑 Удалить фото", callback_data="delete_photo")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_profile_view")]
    ])