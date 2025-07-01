from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command

from keyboards.test import *

start_router = Router()

@start_router.message(Command('start'))
async def start(message: Message):
    await message.answer("👋 Привет Котик и бублик!", reply_markup=main)