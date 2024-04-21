import os
import time
import logging
from dotenv import load_dotenv

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.filters import IsUser
from src.utils import keep_letters_and_digits
from src.database.requests import get_team_name
from src.utils import YandexAPI
from src.bot.structures.keyboards import TO_MENU, USER_MAIN_MENU_BOARD

router = Router()
router.message.filter(IsUser())


async def get_yandex_api_connection():
    load_dotenv()
    yandex_api = YandexAPI(str(os.environ.get('YANDEX_BASE_URL')), str(os.environ.get('YANDEX_OAUTH_TOKEN')))
    connection_status = yandex_api.is_connected()
    logging.info(f"Подключение: {connection_status}")
    return yandex_api


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
    print(file_path)

    timestamp = int(time.time())
    team_name = keep_letters_and_digits(await get_team_name(message.from_user.id))
    filename = f"video_{team_name}_{timestamp}.mp4"

    local_file_path = f"videos/{filename}"
    print(local_file_path)
    local_file_path_full = f"{os.getcwd()}\\videos\\{filename}"
    local_file_path_full = local_file_path_full.replace("\\", "/")
    print(local_file_path_full)
    await bot.download_file(file_path, local_file_path)

    yandex_api = await get_yandex_api_connection()

    YADISK_FOLDER = "/videos"
    # new_folder_response = yandex_api.make_dir(YADISK_FOLDER)
    # logging.info(f"Попытка создания папки: {new_folder_response}")
    json_link = yandex_api.get_upload_link(local_file_path)
    final_upload_link = json_link['href']
    print(final_upload_link)
    upload_response = yandex_api.upload_file(local_file_path, final_upload_link)
    logging.info(f"Попытка загрузки: {upload_response}")

    await message.answer(
        text="✅ Ваше видео загружено и готово для оценивания жюри.",
        reply_markup=USER_MAIN_MENU_BOARD
    )

    # todo: изменять статус загрузки видео в базе данных


@router.message(F.text == "На главное меню")
async def cmd_to_main_menu(message: Message):
    await message.answer(
        text="Главное меню",
        reply_markup=USER_MAIN_MENU_BOARD
    )
