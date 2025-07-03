from states import ProfileState
from database.models import async_session, User
from aiogram.fsm.context import FSMContext

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile

from config.settings import ADMIN_IDS

from keyboards.test import *

@start_router.message(F.text == "✏ Изменить имя")
async def edit_name(message: Message, state: FSMContext):
    await message.answer("Введите новое имя:")
    await state.set_state(ProfileState.editing_name)

@start_router.message(ProfileState.editing_name)
async def save_name(message: Message, state: FSMContext):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.scalar_one_or_none()
        if user:
            user.name = message.text
            await session.commit()
            await message.answer(f"Имя обновлено: {user.name}")
        else:
            await message.answer("Профиль не найден.")
    await state.clear()

@start_router.message(F.text == "🖼 Загрузить фото")
async def ask_photo(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте фото.")
    await state.set_state(ProfileState.waiting_for_photo)

@start_router.message(ProfileState.waiting_for_photo, F.photo)
async def save_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_path = f"photos/{message.from_user.id}.jpg"
    await photo.download(destination=file_path)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.scalar_one_or_none()
        if user:
            user.photo_path = file_path
            await session.commit()
            await message.answer("Фото обновлено.")
        else:
            await message.answer("Пользователь не найден.")
    await state.clear()

@start_router.message(F.text == "🗑 Удалить фото")
async def delete_photo(message: Message):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.scalar_one_or_none()
        if user and user.photo_path:
            import os
            if os.path.exists(user.photo_path):
                os.remove(user.photo_path)
            user.photo_path = None
            await session.commit()
            await message.answer("Фото удалено.")
        else:
            await message.answer("Фото не найдено или не установлено.")

@start_router.message(F.text == "🔙 Назад в меню")
async def handle_back_to_menu(message: Message):
    user = await get_user(message.from_user.id)
    if user.is_admin:
        await message.answer("Вы вернулись в меню", reply_markup=admin_main_menu_keyboard())
    else:
        await message.answer("Вы вернулись в меню", reply_markup=user_main_menu_keyboard())