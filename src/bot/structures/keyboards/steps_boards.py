from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

CANCEL_BUTTON = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Отмена")],
],
    resize_keyboard=True)

CANCEL_SET_BUTTON = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Отменить настройку")],
],
    resize_keyboard=True)

BACK_OR_CANCEL_SET = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Назад")],
    [KeyboardButton(text="Отменить настройку")],
],
    resize_keyboard=True)

CONFIRMATION_BOARD = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Да")],
    [KeyboardButton(text="Назад")],
    [KeyboardButton(text="Отменить настройку")],
],
    resize_keyboard=True)
