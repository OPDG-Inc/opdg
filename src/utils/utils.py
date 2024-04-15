# todo: функция: из фио оставить только имя и отчество для официальных обращений в переписке
#  (см. src/bot/handlers/start.py)
def get_name_and_middle(fio):
    return ' '.join(fio.split()[1:])


def keep_letters_and_digits(input_string):
    """ Функция, которая оставляет в строке только буквы и цифры.
     Используется в логике сохранения видео при обработке названия команды,
     необходима для избежания конфликтов имён при сохранении в систему. """
    allowed_chars = [char for char in input_string if char.isalnum()]
    return ''.join(allowed_chars)
