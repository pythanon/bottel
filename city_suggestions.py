from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from typing import Dict


@logger.catch
def make_cities_kb(city_dict: Dict) -> InlineKeyboardMarkup:
    """
    Функция для создания клавиатуры с предложенными городами.

    :param city_dict: словарь в формате "имя города: id".
    """
    kb = InlineKeyboardMarkup(row_width=1)

    for city_id, city_name in city_dict.items():
        kb.add(InlineKeyboardButton(text=city_name,
                                    callback_data=f'choose_city-{city_id}'))

    return kb
