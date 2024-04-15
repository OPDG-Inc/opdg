from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.filters import IsJury
from src.database.requests import get_team_name
from src.bot.structures.keyboards import TO_MENU, JURY_MAIN_MENU_BOARD

router = Router()
router.message.filter(IsJury())


@router.message(F.text == "Оценка видео")
@router.message(Command(commands=["rate_video"]))
async def cmd_rate_video(message: Message):
    await message.answer(
        text="Сейчас вам предложу видео для оценки...",
        reply_markup=TO_MENU
    )


@router.message(F.text == "На главное меню")
async def cmd_to_main_menu(message: Message):
    await message.answer(
        text="Главное меню",
        reply_markup=JURY_MAIN_MENU_BOARD
    )
