from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger


@logger.catch
def make_history_action_kb() -> InlineKeyboardMarkup:
    """
    Функция для создания клавиатуры с действиями по истории поиска.
    Кнопки: "Посмотреть историю поиска", "Очистить историю".
    """
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text='Посмотреть историю поиска', callback_data='show_history'),
        InlineKeyboardButton(text='Очистить историю', callback_data='clear_history')
    )
    return kb
