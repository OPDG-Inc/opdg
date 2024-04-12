from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU_BOARD = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Проверка статуса")],
    [KeyboardButton(text="Загрузка видео")],
    [KeyboardButton(text="Пользовательское соглашение")],
],
    resize_keyboard=True)
