from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from database.models import History
from loguru import logger
from typing import List


@logger.catch
def output_histories(histories_list: List[History]) -> InlineKeyboardMarkup:
    """
    Функция для создания клавиатуры с историей поиска
    в формате - "дата запроса — команда пользователя — город поиска".

    :param histories_list: список с объектами класса History.
    """
    kb = InlineKeyboardMarkup(row_width=1)
    for i_history in histories_list:
        text = f'{datetime.fromtimestamp(i_history.date).strftime("%d.%m.%Y, %H:%M")} / ' \
               f'{i_history.command} / ' \
               f'{i_history.city}'
        kb.add(InlineKeyboardButton(text=text,
                                    callback_data=f'history-{i_history.id}'))
    return kb
