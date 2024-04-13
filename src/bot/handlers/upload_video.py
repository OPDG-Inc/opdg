from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.filters import IsUser
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
async def cmd_upload_video(bot: Bot, message: Message):
    file_id = message.video.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "video.mp4")
    await message.answer(
        text="Вау, это действительно видео!",
        reply_markup=USER_MAIN_MENU_BOARD
    )


@router.message(F.text == "На главное меню")
async def cmd_to_main_menu(message: Message):
    await message.answer(
        text="Главное меню",
        reply_markup=USER_MAIN_MENU_BOARD
    )
