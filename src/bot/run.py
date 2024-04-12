import os
import asyncio
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import *


async def main():
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(os.environ.get('BOT_TOKEN'))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(reg_team.router,
                       upload_video.router,
                       check_status.router,
                       user_agreement.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
