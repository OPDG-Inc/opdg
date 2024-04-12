from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.bot.filters import IsNotExists
from src.bot.structures.lexicon import (user_agreement_text, text_after_disagreement, just_sent_web_app,
                                        already_registered)
from src.bot.structures.keyboards import (AGREEMENT, SIGN_UP_A_TEAM, MAIN_MENU_BOARD)


router = Router()


@router.message(IsNotExists(), Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(
        text=user_agreement_text,
        reply_markup=AGREEMENT
    )


@router.message(~IsNotExists(), Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(
        text=already_registered,
        reply_markup=MAIN_MENU_BOARD
    )


@router.callback_query(F.data == 'agree')
async def cmd_agree(callback: CallbackQuery):
    await callback.answer('Вам отправлено окно для регистрации команды.')
    await callback.message.edit_text(text=just_sent_web_app,
                                     reply_markup=SIGN_UP_A_TEAM)


@router.callback_query(F.data == 'disagree')
async def cmd_agree(callback: CallbackQuery):
    await callback.answer('что-ж.. гуд бай!')
    await callback.message.edit_text(text=text_after_disagreement)
