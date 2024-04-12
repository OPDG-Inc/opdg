from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.structures.lexicon import user_agreement_text
from src.bot.structures.keyboards import MAIN_MENU_BOARD

router = Router()


@router.message(Command(commands=["user_agreement"]))
async def cmd_start(message: Message):
    await message.answer(
        text=user_agreement_text,
        reply_markup=MAIN_MENU_BOARD
    )
