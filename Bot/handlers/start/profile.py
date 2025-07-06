from handlers.start.states import ProfileState
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto

from keyboards.test import *
from keyboards.profile_keyboard import *
from database.requests import (
    get_user_rank,
    get_user_by_id,
    update_user_name,
    update_user_photo)

profile_router = Router()

@profile_router.message(F.text == "/profile")
@profile_router.message(F.text == "👤 Профиль")
async def handle_profile(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()

    user = await get_user_by_id(message.from_user.id)
    rank = await get_user_rank(message.from_user.id)

    caption = (
        f"🦋 <b>Профиль</b>\n"
        f"<b>├🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>├🦋 Имя:</b> <code>{user.name or '—'}</code>\n\n"
        f"<b>🧊 Статистика</b>\n"
        f"<b>├📚 Пройдено тестов:</b> <code>{user.tests_passed}</code>\n"
        f"<b>├💯 Средняя оценка:</b> <code>{round(user.average_score, 2)}</code>\n"
        f"<b>├⭐ Общие баллы:</b> <code>{round(user.total_score, 2)}</code>\n"
        f"<b>├🏆 Место в рейтинге:</b> <code>#{rank}</code>"
    )

    await state.set_state(ProfileState.viewing)
    await state.update_data(profile_msg_id=None)

    if user.photo_id:
        msg = await message.answer_photo(
            photo=user.photo_id,
            caption=caption,
            reply_markup=profile_keyboard,
            parse_mode="HTML"
        )
    else:
        msg = await message.answer_photo(
            photo=FSInputFile("images/profile.jpg"),
            caption=caption,
            reply_markup=profile_keyboard,
            parse_mode="HTML"
        )

    await state.update_data(profile_msg_id=msg.message_id)


@profile_router.callback_query(F.data == "edit_profile", ProfileState.viewing)
async def edit_profile(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await callback.message.edit_reply_markup(reply_markup=profile_editting_keyboard)

    await callback.message.edit_caption(
        caption="✍️ <b>Редактирование профиля</b>\n\n",
        reply_markup=profile_editting_keyboard,
        parse_mode="HTML"
    )

    await state.set_state(ProfileState.choosing_edit_option)

@profile_router.callback_query(F.data == "edit_name", ProfileState.choosing_edit_option)
async def prompt_edit_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    text = (
        "✍️ <b>Редактирование профиля</b>\n\n"
        "Введите новое имя для отображения:"
    )

    await callback.message.edit_caption(
        caption=text,
        reply_markup=back_to_profile_keyboard,
        parse_mode="HTML"
    )

    await state.set_state(ProfileState.editing_name)

@profile_router.message(ProfileState.editing_name)
async def save_new_name(message: Message, state: FSMContext):
    await update_user_name(message.from_user.id, message.text)

    await message.delete()
    data = await state.get_data()
    profile_msg_id = data.get("profile_msg_id")

    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=profile_msg_id,
        caption="✅ <b>Имя успешно обновлено!</b>",
        reply_markup=back_to_profile_keyboard,
        parse_mode="HTML"
    )

    await state.set_state(ProfileState.viewing)

@profile_router.callback_query(F.data == "edit_photo", ProfileState.choosing_edit_option)
async def choose_photo_action(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await callback.message.edit_caption(
        caption="📷 <b>Редактирование фото профиля</b>",
        reply_markup=choose_action_for_profile_photo,
        parse_mode="HTML"
    )

    await state.set_state(ProfileState.choosing_photo_action)

@profile_router.callback_query(F.data == "upload_photo", ProfileState.choosing_photo_action)
async def prompt_upload_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await callback.message.edit_caption(
        caption="📷 <b>Отправьте новое фото профиля:</b>",
        reply_markup=back_to_profile_keyboard,
        parse_mode="HTML"
    )

    await state.set_state(ProfileState.editing_photo)

@profile_router.message(ProfileState.editing_photo, F.photo)
async def save_uploaded_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await update_user_photo(message.from_user.id, file_id)
    await message.delete()

    user = await get_user_by_id(message.from_user.id)
    rank = await get_user_rank(user.id)

    caption = (
        f"🦋 <b>Профиль</b>\n"
        f"<b>├🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>├🦋 Имя:</b> <code>{user.name or '—'}</code>\n\n"
        f"<b>🧊 Статистика</b>\n"
        f"<b>├📚 Пройдено тестов:</b> <code>{user.tests_passed}</code>\n"
        f"<b>├💯 Средняя оценка:</b> <code>{round(user.average_score, 2)}</code>\n"
        f"<b>├⭐ Общие баллы:</b> <code>{round(user.total_score, 2)}</code>\n"
        f"<b>├🏆 Место в рейтинге:</b> <code>#{rank}</code>\n\n"
        f"✅ <b>Фото успешно обновлено!</b>"
    )

    data = await state.get_data()
    profile_msg_id = data.get("profile_msg_id")

    await message.bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=profile_msg_id,
        media=InputMediaPhoto(
            media=file_id,
            caption=caption,
            parse_mode="HTML"
        ),
        reply_markup=profile_keyboard
    )

    await state.set_state(ProfileState.viewing)

@profile_router.callback_query(F.data == "delete_photo", ProfileState.choosing_photo_action)
async def delete_profile_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await update_user_photo(callback.from_user.id, None)

    user = await get_user_by_id(callback.from_user.id)
    rank = await get_user_rank(user.id)

    caption = (
        f"🦋 <b>Профиль</b>\n"
        f"<b>├🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>├🦋 Имя:</b> <code>{user.name or '—'}</code>\n\n"
        f"<b>🧊 Статистика</b>\n"
        f"<b>├📚 Пройдено тестов:</b> <code>{user.tests_passed}</code>\n"
        f"<b>├💯 Средняя оценка:</b> <code>{round(user.average_score, 2)}</code>\n"
        f"<b>├⭐ Общие баллы:</b> <code>{round(user.total_score, 2)}</code>\n"
        f"<b>├🏆 Место в рейтинге:</b> <code>#{rank}</code>\n\n"
        f"🗑 <b>Фото профиля удалено</b>"
    )

    data = await state.get_data()
    profile_msg_id = data.get("profile_msg_id")

    await callback.bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=profile_msg_id,
        media=InputMediaPhoto(
            media=FSInputFile("images/profile.jpg"),
            caption=caption,
            parse_mode="HTML"
        ),
        reply_markup=profile_keyboard
    )

    await state.set_state(ProfileState.viewing)


@profile_router.callback_query(F.data == "back_to_main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user = await get_user_by_id(callback.from_user.id)
    keyboard = admin_main_menu_keyboard() if user.is_admin else user_main_menu_keyboard()
    await callback.message.answer_photo(
        FSInputFile("images/Main_menu.png"), 
        caption="👋 Вы вернулись в главное меню!", 
        reply_markup=keyboard)
    await state.clear()

@profile_router.callback_query(F.data == "back_to_profile_view")
async def back_to_profile_view(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user = await get_user_by_id(callback.from_user.id)
    rank = await get_user_rank(user.id)

    caption = (
        f"🦋 <b>Профиль</b>\n"
        f"<b>├🆔 ID:</b> <code>{user.id}</code>\n"
        f"<b>├🦋 Имя:</b> <code>{user.name or '—'}</code>\n\n"
        f"<b>🧊 Статистика</b>\n"
        f"<b>├📚 Пройдено тестов:</b> <code>{user.tests_passed}</code>\n"
        f"<b>├💯 Средняя оценка:</b> <code>{round(user.average_score, 2)}</code>\n"
        f"<b>├⭐ Общие баллы:</b> <code>{round(user.total_score, 2)}</code>\n"
        f"<b>├🏆 Место в рейтинге:</b> <code>#{rank}</code>"
    )

    await callback.message.edit_caption(
        caption=caption,
        reply_markup=profile_keyboard,
        parse_mode="HTML"
    )

    await state.set_state(ProfileState.viewing)

