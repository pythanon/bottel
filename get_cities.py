import json
from .api_request import rapid_api_request
from loguru import logger
from telebot.types import Message
from typing import Dict, Union


@logger.catch
def get_city_dict(message: Message) -> Union[Dict, None]:
    """
    Функция для парсинга предлагаемых городов, в соответствии с городом пользователя.
    1. Формирует параметры запроса к API.
    2. Получает ответ от API.
    3. Собирает названия город и их id в словарь city_dict.

    :param message: сообщение Телеграм.
    """

    input_city = message.text
    querystring = {"q": input_city, "locale": "ru_RU"}
    response = rapid_api_request(method_type="GET",
                                 endpoint='locations/v3/search',
                                 params=querystring)
    if response:
        json_dict = json.loads(response.text)
        json_locations = json_dict.get('sr')
        city_dict = dict()

        if json_locations:
            for i_city in json_locations:
                if i_city.get('type') == 'CITY':
                    city_name = i_city.get('regionNames').get('displayName')
                    city_id = i_city.get('gaiaId')
                    city_dict[city_id] = city_name
            return city_dict

        else:
            return None
    else:
        return None
