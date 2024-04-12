from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.structures.keyboards import MAIN_MENU_BOARD

router = Router()


@router.message(Command(commands=["check_status"]))
async def cmd_start(message: Message):
    await message.answer(
        text="Ваше видео ещё не проверено.",
        reply_markup=MAIN_MENU_BOARD
    )
