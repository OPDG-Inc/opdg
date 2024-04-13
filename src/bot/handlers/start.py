from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject

from src.bot.filters import IsNotExists
from src.bot.structures.lexicon import (user_agreement_text, text_after_disagreement, just_sent_web_app,
                                        already_registered)
from src.bot.structures.keyboards import (AGREEMENT, SIGN_UP_A_TEAM, MAIN_MENU_BOARD)
from src.database.requests import (get_jury_by_link_code,
                                   get_jury_status,
                                   set_jury_status_to_registered,
                                   get_jury_name)


router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start_link(message: Message, command: CommandObject):
    args = command.args
    link_type, code = args.split('_')
    if link_type == 'jury' and code is not None:
        jury_id = await get_jury_by_link_code(code)
    jury_status = await get_jury_status(jury_id)
    if jury_status == 'waiting':
        await set_jury_status_to_registered(jury_id)
    jury_name = await get_jury_name(jury_id)
    jury_name = ' '.join(jury_name.split()[1:])
    await message.answer(
        text=f"{jury_name}, вы зарегистрировались как жюри.",
        reply_markup=MAIN_MENU_BOARD
    )


@router.message(IsNotExists(), Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(
        text=user_agreement_text,
        reply_markup=AGREEMENT
    )


@router.message(~IsNotExists(), Command(commands=["start"]))
async def cmd_start_exists(message: Message):
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
async def cmd_disagree(callback: CallbackQuery):
    await callback.answer('что-ж.. гуд бай!')
    await callback.message.edit_text(text=text_after_disagreement)
