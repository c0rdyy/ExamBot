from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

API_TOKEN = os.getenv('API_TOKEN')

bot = Bot(API_TOKEN)
dp = Dispatcher(bot=bot)