from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

USER_MAIN_MENU_BOARD = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Проверка результатов")],
    [KeyboardButton(text="Загрузка видео")],
    [KeyboardButton(text="Пользовательское соглашение")],
],
    resize_keyboard=True)

JURY_MAIN_MENU_BOARD = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Оценка видео")],
],
    resize_keyboard=True)
