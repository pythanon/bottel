from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger


@logger.catch
def make_yes_or_no_kb() -> InlineKeyboardMarkup:
    """
    Функция для создания клавиатуры
    с выбором ответа о необходимости вывода фото.
    Кнопки: "Да", "Нет".
    """
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text='Да', callback_data=f'need_photo-YES'))
    kb.add(InlineKeyboardButton(text='Нет', callback_data=f'need_photo-NO'))

    return kb
