from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


AGREEMENT = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Принимаю',
                          callback_data='agree')],
    [InlineKeyboardButton(text='❌ Отклоняю',
                          callback_data='disagree')],
])
