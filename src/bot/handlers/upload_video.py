from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.structures.keyboards import TO_MENU, USER_MAIN_MENU_BOARD

router = Router()


@router.message(Command(commands=["upload_video"]))
@router.message(F.text == "Загрузка видео")
async def cmd_upload_video(message: Message):
    await message.answer(
        text="Пришли видеоролик размером не более 2-х Гб.\n\n"
             "Если Ваше творение весит больше, то воспользуйтесь бесплатным сервисом сжатьбесплатновидео.ру",
        reply_markup=TO_MENU
    )


@router.message(F.text == "На главное меню")
async def cmd_to_main_menu(message: Message):
    await message.answer(
        text="Главное меню.",
        reply_markup=USER_MAIN_MENU_BOARD
    )
