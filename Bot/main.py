import asyncio

from config.bot_config import dp, bot, routers
from handlers.start.start import *
from database.models import async_main

async def main():
    await async_main()

    for router in routers:
        dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')