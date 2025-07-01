from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv
from aiogram.fsm.storage.memory import MemoryStorage
import os

from handlers.start.start import start_router

load_dotenv(find_dotenv())

API_TOKEN = os.getenv('API_TOKEN')

bot = Bot(API_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
routers = [start_router]