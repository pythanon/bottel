import json
from .api_request import rapid_api_request
from config_data.config import payload, payload_for_details
from loguru import logger
from typing import Dict, List, Union
from copy import deepcopy


@logger.catch
def get_hotels_info(data: Dict) -> Union[List, None]:
    """
    Функция для парсинга отелей и сбора результатов в список словарей с параметрами отелей.
    1. Собирает параметры запроса к API "new_payload" с помощью функции "build_payload".
    2. Выполняет запрос.
    3. Если запрос успешен, собирает необходимые параметры для вывода отелей в словарь "hotel_dict"
    и добавляет словарь в список "hotels_list".
    4. Инициализирует функцию "add_photos_and_address"
    для добавления адреса и фото (если это необходимо) в итоговый список отелей result_list.

    :param data: база параметров пользователя.
    """
    try:
        new_payload = build_payload(data=data)
        response = rapid_api_request(method_type='POST',
                                     endpoint='properties/v2/list',
                                     params=new_payload)
        if response:
            json_dict = json.loads(response.text)
            if not json_dict.get('errors'):
                property_list = json_dict.get('data').get('propertySearch').get('properties')
                hotels_list = list()
                hotels_amount = int(data.get('hotels_amount'))
                user_max_distance = int(data.get('distance', 0))

                if data.get('command') == 'highprice':
                    property_list.reverse()

                for i_hotel in property_list[:hotels_amount]:
                    distance = round(i_hotel.get('destinationInfo').get('distanceFromDestination').get('value')
                                     * 1.609, 1)

                    if data.get('command') == 'bestdeal':
                        if distance > user_max_distance:
                            continue

                    hotel_dict = dict()
                    hotel_dict['id'] = i_hotel.get('id')
                    hotel_dict['name'] = i_hotel.get('name')
                    hotel_dict['distance'] = distance
                    hotel_dict['price'] = round(i_hotel.get('price').get('lead').get('amount'), 1)
                    hotel_dict['link'] = f'https://www.hotels.com/h{hotel_dict.get("id")}.Hotel-Information'
                    hotels_list.append(hotel_dict)

                need_photo = data.get('need_photo')
                photo_amount = int(data.get('photo_amount', 0))
                result_list = add_photos_and_address(hotels_list=hotels_list,
                                                     photo_amount=photo_amount,
                                                     need_photo=need_photo)

                return result_list

            else:
                raise ValueError
        else:
            raise ValueError

    except ValueError:
        return None


@logger.catch
def add_photos_and_address(hotels_list: List[dict], photo_amount: int, need_photo: bool) -> Union[List, None]:
    """
    Функция для добавления адреса и фото к результатам поиска отелей.
    1. Собирает параметры запроса к API "new_payload".
    2. Добавляет адрес в словарь с параметрами отеля.
    3. Если нужны фото, парсит и сохраняет url фото в словарь с параметрами отеля.

    :param hotels_list: список отелей с параметрами.
    :param photo_amount: кол-во фото.
    :param need_photo: необходимость вывода фото.
    """
    new_payload = deepcopy(payload_for_details)
    result_list = list()

    for i_hotel in hotels_list:
        new_payload['propertyId'] = i_hotel.get('id')
        response = rapid_api_request(method_type='POST',
                                     endpoint='properties/v2/detail',
                                     params=new_payload)
        if response:
            json_dict = json.loads(response.text)

            i_hotel['address'] = json_dict.get('data').get('propertyInfo').get('summary')\
                .get('location').get('address').get('addressLine')

            if need_photo:
                images_list = json_dict.get('data').get('propertyInfo').get('propertyGallery').get('images')
                images_url_list = list()
                for i_image in images_list[:photo_amount]:
                    if i_image.get('image').get('url'):
                        image_url = i_image['image']['url']
                        images_url_list.append(image_url)
                i_hotel['images_list'] = images_url_list

            result_list.append(i_hotel)
        else:
            return None

    return result_list


@logger.catch
def build_payload(data: Dict) -> Dict:
    """
    Функция для построения параметров запроса к API (payload)
    в зависимости от команды пользователя и критериев поиска отелей.

    :param data: база параметров пользователя.
    """
    new_payload = deepcopy(payload)

    new_payload['destination']['regionId'] = data.get('city_id')
    new_payload['sort'] = data.get('sort_type')

    year, month, day = str(data.get('check_in')).split('-')
    new_payload['checkInDate']['year'] = int(year)
    new_payload['checkInDate']['month'] = int(month)
    new_payload['checkInDate']['day'] = int(day)

    year, month, day = str(data.get('check_out')).split('-')
    new_payload['checkOutDate']['year'] = int(year)
    new_payload['checkOutDate']['month'] = int(month)
    new_payload['checkOutDate']['day'] = int(day)

    new_payload['sort'] = data.get('sort_type')

    if data.get('command') == 'bestdeal':
        new_payload['filters']['price'] = dict()
        new_payload['filters']['price']['max'] = int(data.get('max_price'))
        new_payload['filters']['price']['min'] = int(data.get('min_price'))
    else:
        new_payload['filters'].pop('price')

    return new_payload
