from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()


@router.message(Command(commands=["upload_video"]))
async def cmd_start(message: Message):
    await message.answer(
        text="Начало",
        reply_markup=ReplyKeyboardRemove()
    )
