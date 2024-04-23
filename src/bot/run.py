import os
import asyncio
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import *
from middlewares import SkipSideUser


async def main():
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(os.environ.get('BOT_TOKEN'))
    dp = Dispatcher(storage=MemoryStorage())

    router_service = Router()  # все роутеры, кроме start
    router_service.include_routers(upload_video.router,
                                   check_results.router,
                                   rate_video.router,
                                   user_agreement.router)
    router_service.message.outer_middleware(SkipSideUser())

    dp.include_routers(start.router, router_service)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
