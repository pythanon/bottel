from loader import bot
from .get_hotels_info import get_hotels_info
from telebot.types import InputMediaPhoto, Message
from loguru import logger
from database.db_sqlite import save_user_to_db, save_history_to_db
from typing import Dict


@logger.catch
def output_hotels_info(data: Dict, message: Message) -> None:
    """
    Функция для вывода результатов поиска отелей.
    1. Присваивает списку "hotels_list" значение функции "get_hotels_info".
    2. Если список != None, формирует текст сообщения в Телеграм и добавляет его в БД.
    3. Если список url фото отеля не пустой, формирует текст сообщения в Телеграм вместе с фото.
    4. Сохраняет пользователя в БД с помощью функции "save_user_to_db".
    5. Сохраняет историю поиска "results_for_db" в БД с помощью функции "save_user_to_db".

    :param data: база параметров пользователя.
    :param message: сообщение Телеграм.
    """
    hotels_list = get_hotels_info(data=data)
    if hotels_list:
        results_for_db = list()
        for i_hotel in hotels_list:
            text = f'🏨 <b>{i_hotel.get("name")}</b>\n' \
                   f'📍 Адрес: <b>{i_hotel.get("address")}</b>\n' \
                   f'📏 Расстояние от центра: <b>{i_hotel.get("distance")}</b> км.\n' \
                   f'💵 Цена за ночь: <b>{i_hotel.get("price")}$</b>\n' \
                   f'💰 Приблизительная стоимость поездки: ' \
                   f'<b>{round(i_hotel.get("price", 0) * data.get("days_amount", 0))}$</b>\n' \
                   f'<b>Бронь по ссылке</b> 👇\n{i_hotel.get("link")}\n'
            results_for_db.append(text)

            if i_hotel.get('images_list'):
                photo_urls = i_hotel.get('images_list')
                photos = [
                    InputMediaPhoto(media=url, caption=text, parse_mode='html') if index == 0 else InputMediaPhoto(
                        media=url)
                    for index, url in enumerate(photo_urls)
                ]
                bot.send_media_group(message.chat.id, photos)
            else:
                bot.send_message(message.chat.id, text, parse_mode='html')

        save_user_to_db(username=message.from_user.username)
        save_history_to_db(username=message.from_user.username, command=data.get('command'), city=data.get('city_name'),
                           hotels_list=results_for_db)
        bot.send_message(chat_id=message.chat.id,
                         text='🙃 Вывел все, что нашел!\n'
                              '👉 Воспользуйся командой /help и посмотри, что еще можно сделать.',
                         parse_mode='html')

    else:
        bot.send_message(message.chat.id, '😔 К сожалению, не нашел отели по заданным критериям.\n'
                                          '🙏 Попробуй задать другие параметры поиска ➡ /help')

    bot.delete_state(message.from_user.id, message.chat.id)
