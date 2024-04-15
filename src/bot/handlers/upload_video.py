import time

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.filters import IsUser
from src.utils import keep_letters_and_digits
from src.database.requests import get_team_name
from src.bot.structures.keyboards import TO_MENU, USER_MAIN_MENU_BOARD

router = Router()
router.message.filter(IsUser())


@router.message(Command(commands=["upload_video"]))
@router.message(F.text == "Загрузка видео")
async def cmd_upload_video(message: Message):
    await message.answer(
        text="Пришли видеоролик размером не более 2-х Гб.\n\n"
             "Если Ваше творение весит больше, то воспользуйтесь бесплатным сервисом сжатьбесплатновидео.ру",
        reply_markup=TO_MENU
    )


@router.message(F.video)
async def cmd_upload_video(message: Message, bot: Bot):
    await message.answer(text="Подождите, сохраняю ваше видео...")
    file_id = message.video.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    timestamp = int(time.time())
    team_name = keep_letters_and_digits(await get_team_name(message.from_user.id))
    filename = f"video_{team_name}_{timestamp}.mp4"

    await bot.download_file(file_path, filename)
    await message.answer(
        text="Ваше видео сохранено.",
        reply_markup=USER_MAIN_MENU_BOARD
    )


@router.message(F.text == "На главное меню")
async def cmd_to_main_menu(message: Message):
    await message.answer(
        text="Главное меню",
        reply_markup=USER_MAIN_MENU_BOARD
    )
