from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.structures.keyboards import SIGN_UP_A_TEAM

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(
        text="Вам отправлено окно для регистрации команды.",
        reply_markup=SIGN_UP_A_TEAM
    )

# todo: пользовательское соглашение
