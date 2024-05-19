from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove)

from src.bot.filters import IsJury
from src.database.requests import (get_rated_videos_by_jury,
                                   get_team_name_by_group_id,
                                   get_team_video_link,
                                   get_all_group_with_uploaded_videos)
from src.bot.structures.keyboards import JURY_MAIN_MENU_BOARD, TO_MENU

router = Router()
router.message.filter(IsJury())


@router.message(F.text == "Оценка видео")
@router.message(Command(commands=["rate_video"]))
async def cmd_rate_video(message: Message):
    # todo: массив group_id уже оценённых этим жюри видео
    already_rated_videos = await get_rated_videos_by_jury(message.from_user.id)
    all_videos = await get_all_group_with_uploaded_videos()
    await message.answer(
        text=f"{already_rated_videos}",
        reply_markup=ReplyKeyboardRemove()
    )
    # todo: сообщение о том, сколько осталось оценить видео
    await message.answer(
        text=f"{len(all_videos) - len(already_rated_videos)}",
        reply_markup=ReplyKeyboardRemove()
    )
    # todo: выбираем следующее неоценённое -> group_id
    group_id = 3
    team_name = await get_team_name_by_group_id(group_id)
    video_url = await get_team_video_link(group_id)
    RATE_VIDEO_BTN = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text="Оценить видео",
            url=f"https://t.me/vshpm_event_bot/super?startapp=rate{group_id}")],
    ])
    await message.answer(
        text=f"Команда: {team_name}\n\nВидео: {video_url}",
        reply_markup=RATE_VIDEO_BTN
    )


@router.message(F.text == "На главное меню")
async def cmd_to_main_menu(message: Message):
    await message.answer(
        text="Главное меню",
        reply_markup=JURY_MAIN_MENU_BOARD
    )
