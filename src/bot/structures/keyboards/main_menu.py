from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU_BOARD = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Проверка заявки")],
    [KeyboardButton(text="Загрузка видео")],
],
    resize_keyboard=True)
