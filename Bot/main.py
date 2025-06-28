import asyncio

from config.bot_config import dp, bot
from handlers.start.start import *

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())