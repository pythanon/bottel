from config_data.config import headers
from loguru import logger
import requests
from requests.models import Response
from typing import Dict, Union


@logger.catch
def rapid_api_request(method_type: str, endpoint: str, params: Dict) -> Union[Response, None]:
    """
    Функция для формирования url запроса с эндпоинтом.
    В зависимости от типа запроса возвращает результат функции "get_request" или "post_request".
    :param method_type: тип запроса.
    :param endpoint: энпоинт запроса.
    :param params: querystring с параметрами поиска.
    """
    url = f"https://hotels4.p.rapidapi.com/{endpoint}"
    if method_type == 'GET':
        return get_request(url=url, params=params)
    else:
        return post_request(url=url, payload=params)


@logger.catch
def get_request(url: str, params: Dict) -> Union[Response, None]:
    """
    Функция для выполнения GET запроса к API.
    Если код ответа == 200, возвращает ответ, в противном случае - None.
    :param url: url запроса.
    :param params: querystring с параметрами поиска.
    """
    try:
        response = requests.request(method='GET',
                                    url=url,
                                    headers=headers,
                                    params=params,
                                    timeout=15)

        if response.status_code == requests.codes.ok:
            return response

    except Exception:
        return None


@logger.catch
def post_request(url: str, payload: Dict) -> Union[Response, None]:
    """
    Функция для выполнения POST запроса к API.
    Если код ответа == 200, возвращает ответ, в противном случае - None.
    :param url: url запроса.
    :param payload: словарь с параметрами запроса.
    """
    try:
        response = requests.request(method='POST',
                                    url=url,
                                    json=payload,
                                    headers=headers,
                                    timeout=15)

        if response.status_code == requests.codes.ok:
            return response

    except Exception:
        return None
