from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command

from config.admin_ids import ADMIN_IDS
from keyboards.test import *

start_router = Router()

@start_router.message(F.text == "/start")
async def cmd_start(message: Message):
    if message.from_user.id in ADMIN_IDS:
        keyboard = admin_main_menu_keyboard()
    else:
        keyboard = user_main_menu_keyboard()

    await message.answer("Добро пожаловать в главное меню! Выберите действие:", reply_markup=keyboard)

@start_router.message(F.text == "🧠 Начать тест")
async def handle_test(message: Message):
    await message.answer("Выберите уровень сложности теста:")

@start_router.message(F.text == "👤 Профиль")
async def handle_profile(message: Message):
    await message.answer("Ваш профиль:")

@start_router.message(F.text == "🏆 Рейтинг")
async def handle_rating(message: Message):
    await message.answer("Текущий рейтинг:")

@start_router.message(F.text == "🛠 Админ-панель")
async def handle_admin(message: Message):
    await message.answer("Панель администратора:")

@start_router.message(F.text == "/help")
@start_router.message(F.text == "❓ Помощь")
async def handle_help(message: Message):
    help_text = (
        "ℹ️ *О боте:*\n"
        "Этот бот предназначен для прохождения тестов по объектно-ориентированному программированию (ООП).\n\n"
        "📌 *Команды и кнопки:*\n"
        "/start - pапустить бота.\n"
        "/test — начать тест.\n"
        "/profile — открыть профиль.\n"
        "/rate — посмотреть свой рейтинг среди других пользователей.\n"
        "/help — показать справку по командам.\n\n"
    )
    await message.answer(help_text, parse_mode="Markdown")

