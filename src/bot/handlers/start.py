from aiogram import F, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from src.utils import get_name_and_middle
from src.bot.filters import IsUser, IsJury
from src.bot.structures.lexicon import (user_agreement_text, text_after_disagreement, just_sent_web_app,
                                        user_already_registered, jury_already_registered, user_reg_but_jury,)
from src.bot.structures.keyboards import (AGREEMENT, SIGN_UP_A_TEAM, USER_MAIN_MENU_BOARD, JURY_MAIN_MENU_BOARD,)
from src.database.requests import (get_jury_by_link_code, get_jury_status, set_jury_status_to_registered,
                                   get_jury_name, is_jury_correlate_with_code,)


router = Router()


@router.message(IsJury(), CommandStart(deep_link=True))
async def cmd_start_jury_link(message: Message, command: CommandObject):
    args = command.args
    link_type, code = args.split('_')
    jury_id = None

    if link_type == 'jury' and code is not None:
        jury_id = await get_jury_by_link_code(code)

    if jury_id is None:
        await message.answer(
            text="Код ссылки недействителен или произошла ошибка при поиске жюри.",
            reply_markup=ReplyKeyboardRemove()
        )

    jury_status = await get_jury_status(jury_id)
    if jury_status not in ('waiting', 'registered',):
        print("Ошибка в базе данных: в колонке status неизвестных статус")
        return

    if jury_status == 'registered':
        await message.answer(
            text=jury_already_registered,
            reply_markup=JURY_MAIN_MENU_BOARD
        )
        return

    if jury_status == 'waiting':
        is_correct_jury = await is_jury_correlate_with_code(jury_id=jury_id, telegram_id=message.from_user.id)

        if not is_correct_jury:
            await message.answer(
                text="Ваш профиль телеграм не соответствует вашей ссылке.",
                reply_markup=ReplyKeyboardRemove()
            )
            return

        await set_jury_status_to_registered(jury_id)

    jury_name = await get_jury_name(jury_id)
    if jury_name == '' or jury_name is None:
        jury_name = 'Неизвестный'
    else:
        jury_name = get_name_and_middle(jury_name)
    await message.answer(
        text=f"{jury_name}, вы зарегистрировались как жюри.",
        reply_markup=JURY_MAIN_MENU_BOARD
    )


@router.message(~IsUser(), CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        text=user_agreement_text,
        reply_markup=AGREEMENT
    )


@router.message(IsJury(), CommandStart())
async def cmd_start_jury_already_exists(message: Message):
    await message.answer(
        text=user_reg_but_jury,
        reply_markup=JURY_MAIN_MENU_BOARD
    )


@router.message(IsUser(), CommandStart())
async def cmd_start_user_already_exists(message: Message):
    await message.answer(
        text=user_already_registered,
        reply_markup=USER_MAIN_MENU_BOARD
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
