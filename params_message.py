from loguru import logger
from typing import Dict


@logger.catch
def search_params_output(data: Dict) -> str:
    """
    Функция для формирования сообщения о критериях поиска отелей.

    :param data: база параметров пользователя.
    """
    photo_amount = data.get('photo_amount')
    command = data.get('command')
    sort_type = ''
    bestdeal_text = ''

    if command == 'lowprice':
        sort_type = 'топ дешевых отелей'
    elif command == 'highprice':
        sort_type = 'топ дорогих отелей'
    elif command == 'bestdeal':
        sort_type = 'отели по цене и расположению от центра'
        bestdeal_text = f'💵 Цена от: {data.get("min_price")}$ до {data.get("max_price")}$\n' \
                        f'📏 Расстояние от центра: {data.get("distance")}'

    text = f'👇 Уже ищу отели по этим параметрам:\n\n' \
           f'🏙 Город: {data.get("city_name")}\n' \
           f'🏨 Вывести отелей: {data.get("hotels_amount")} шт.\n' \
           f'➡ Дата заезда: {data.get("check_in")}\n' \
           f'⬅ Дата выезда: {data.get("check_out")}\n' \
           f'🗓 Количество дней: {data.get("days_amount")}\n' \
           f'{f"🖼 Понадобится фото: {photo_amount} шт." if data.get("need_photo") else f"🖼 Фото не понадобятся"}\n' \
           f'↕️ Сортировка: {sort_type}\n'

    return text + bestdeal_text
