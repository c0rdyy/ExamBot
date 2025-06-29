from aiogram import F
from aiogram.types import Message

from config.bot_config import dp

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("👋 Привет бублик!")