from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.structures.keyboards import USER_MAIN_MENU_BOARD

router = Router()


@router.message(Command(commands=["check_status"]))
@router.message(F.text == "Проверка статуса")
async def cmd_check_status(message: Message):
    await message.answer(
        text="Ваше видео ещё не проверено.",
        reply_markup=USER_MAIN_MENU_BOARD
    )
