from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from config.bot_config import ADMIN_IDS
from keyboards.admin_panel_keyboard import admin_menu

admin_router = Router()

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.answer("🛠 Админ-панель", reply_markup=admin_menu)
