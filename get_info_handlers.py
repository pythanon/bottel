from loader import bot
from telebot.types import Message, CallbackQuery
from states.user_states import UserStates
from utils.get_cities import get_city_dict
from keyboards.inline import city_suggestions, need_photo
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta, datetime
from utils.params_message import search_params_output
from utils.output_hotels import output_hotels_info
from loguru import logger
from copy import deepcopy


@bot.message_handler(state=UserStates.cities_dict)
@logger.catch
def get_city(message: Message) -> None:
    """
    Хендлер, ожидающий ввод города от пользователя.
    1. Собирает словарь предложенных городов с помощью функции "get_city_dict".
    2. Если город найден, передает словарь "city_dict" в "data",
    отправляет сообщение с инлайн-клавиатурой предложенных городов.

    :param message: сообщение Телеграм
    """
    chat_id = message.chat.id
    bot.send_message(chat_id, '🔎 Ищу город...')

    if not message.text.isdigit():
        city_dict = get_city_dict(message=message)
        if city_dict:
            with bot.retrieve_data(chat_id, chat_id) as data:
                data['cities_dict'] = city_dict
            kb = city_suggestions.make_cities_kb(city_dict)
            bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            bot.send_message(chat_id, '⬇ Пожалуйста, уточни:', reply_markup=kb)
        else:
            bot.send_message(chat_id, '❕ Не нашел город. Пожалуйста, введи еще раз.')
    else:
        bot.send_message(chat_id, '❕ В названии города должны быть буквы.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_city-'))
@logger.catch
def city_clarification(call: CallbackQuery) -> None:
    """
    Хендлер, ожидающий уточнения города от пользователя.
    1. Передает имя и id города в "data".
    2. Отправляет сообщение с инлайн-клавиатурой календаря.

    :param call: отклик клавиатуры.
    """
    chat_id = call.message.chat.id
    city_id = call.data.replace('choose_city-', '')

    with bot.retrieve_data(chat_id, chat_id) as data:
        data['city_name'] = data.get('cities_dict').get(city_id)
        data['city_id'] = city_id

    bot.edit_message_text(text=f'✅ Выбран город: {data.get("city_name")}',
                          chat_id=chat_id,
                          message_id=call.message.message_id)

    calendar, step = DetailedTelegramCalendar(min_date=date.today()).build()
    bot.send_message(chat_id=chat_id,
                     text=f"➡ Дата заезда:",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
@logger.catch
def get_dates(call: CallbackQuery) -> None:
    """
    Хендлер для действий в инлайн-календаре.
    1. Записывает даты заселения и выселения в "data".
    2. При наличии записей 'check_in' и 'check_out' в "data",
    выводит инлайн-клавиатуру с вопросом о необходимости вывода фото для отелей.
    :param call: отклик клавиатуры.
    """
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id

    with bot.retrieve_data(chat_id, chat_id) as data:
        if not data.get('check_in'):
            min_date = date.today()
        else:
            min_date = data.get('check_in') + timedelta(1)

        result, key, step = DetailedTelegramCalendar(min_date=min_date,
                                                     locale='ru').process(call.data)

        if not result and key:
            if LSTEP[step] == 'year':
                cur_step = 'год'
            elif LSTEP[step] == 'month':
                cur_step = 'месяц'
            else:
                cur_step = 'день'
            bot.edit_message_text(text=f"Выбери {cur_step}",
                                  chat_id=chat_id,
                                  message_id=message_id,
                                  reply_markup=key)
        elif result:
            if not data.get('check_in'):
                data['check_in'] = result
                calendar, step = DetailedTelegramCalendar(min_date=result + timedelta(2)).build()
                bot.edit_message_text(text=f"⬅ Дата выезда:",
                                      chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=calendar)
            else:
                data['check_out'] = result
                bot.edit_message_text(text=f'➡ Дата заезда: {data.get("check_in")}\n'
                                           f'⬅ Дата выезда: {data.get("check_out")}',
                                      chat_id=chat_id,
                                      message_id=message_id)

                check_in_date = datetime.strptime(str(data.get('check_in')), "%Y-%m-%d")
                check_out_date = datetime.strptime(str(data.get('check_out')), "%Y-%m-%d")
                days_amount = str(check_out_date - check_in_date).split()
                data['days_amount'] = int(days_amount[0])

                kb = need_photo.make_yes_or_no_kb()
                bot.send_message(chat_id=user_id,
                                 text='📷 Загрузить фото отелей?',
                                 reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith('need_photo-'))
@logger.catch
def photo_choice(call: CallbackQuery) -> None:
    """
    Хендлер, ожидающий ответ по выводу фото для отелей.
    1. Записывает даты заселения и выселения в "data".
    2. Если ответ - "да", записывает True в data['need_photo'] и запрашивает кол-во фото.
    3. Если ответ - "нет", записывает False в data['need_photo'] и запрашивает кол-во отелей.

    :param call: отклик клавиатуры.
    """
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id

    choice = call.data.replace('need_photo-', '')
    with bot.retrieve_data(chat_id, chat_id) as data:
        if choice == 'YES':
            data['need_photo'] = True
            bot.set_state(user_id=user_id,
                          state=UserStates.photo_amount,
                          chat_id=chat_id)
            bot.edit_message_text(text='🖼 Сколько фото показать для каждого отеля? (максимум 10)',
                                  chat_id=chat_id,
                                  message_id=message_id)
        else:
            data['need_photo'] = False
            bot.set_state(user_id=user_id,
                          state=UserStates.hotels_amount,
                          chat_id=chat_id)
            bot.edit_message_text(text='✅ Фото не понадобятся.',
                                  chat_id=chat_id,
                                  message_id=message_id)
            bot.send_message(chat_id=chat_id, text='🏨 Сколько отелей показать? (максимум 10).')


@bot.message_handler(state=UserStates.photo_amount)
@logger.catch
def get_photo_amount(message: Message) -> None:
    """
    Хендлер, ожидающий кол-во фото для отелей от пользователя.
    1. Проверяет соответствие сообщения к допустимому максимуму.
    2. Если проверка пройдена, запрашивает кол-во отелей.

    :param message: сообщение Телеграм.
    """
    user_num = message.text
    chat_id = message.chat.id
    message_id = message.message_id

    if user_num.isdigit() and 1 <= int(user_num) <= 10:
        with bot.retrieve_data(chat_id, chat_id) as data:
            data['photo_amount'] = user_num
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            bot.send_message(chat_id=chat_id,
                             text=f'✅ Показать фото на каждый отель: {user_num} шт.')
            bot.set_state(user_id=message.from_user.id,
                          state=UserStates.hotels_amount,
                          chat_id=chat_id)
            bot.send_message(chat_id=chat_id,
                             text='🏨 Сколько отелей показать? (максимум 10).')
    else:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_message(chat_id=chat_id, text='❕ Ответ должен быть числом от 1 до 10.')


@bot.message_handler(state=UserStates.hotels_amount)
@logger.catch
def get_hotels_amount(message: Message) -> None:
    """
    Хендлер, ожидающий кол-во отелей от пользователя.
    1. Проверяет соответствие сообщения к допустимому максимуму.
    2. Если команда пользователя - "lowprice" или "highprice",
    отправляет сообщение с параметрами поиска и инициализирует функцию "output_hotels_info"
    3. Если команда пользователя - "bestdeal", запрашивает минимальную цену отеля за ночь.

    :param message: сообщение Телеграм.
    """
    user_num = message.text
    chat_id = message.chat.id
    message_id = message.message_id

    if user_num.isdigit() and 1 <= int(user_num) <= 10:
        with bot.retrieve_data(chat_id, chat_id) as data:
            data['hotels_amount'] = user_num
            data_dict = deepcopy(data)

        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_message(chat_id=chat_id,
                         text=f'✅ Показать отелей: {data.get("hotels_amount")} шт.')

        if data_dict.get('command') in ('lowprice', 'highprice'):
            params_text = search_params_output(data=data_dict)
            bot.send_message(chat_id=chat_id,
                             text=params_text)
            output_hotels_info(data=data_dict, message=message)

        else:
            bot.set_state(user_id=message.from_user.id,
                          state=UserStates.price_range,
                          chat_id=chat_id)
            bot.send_message(chat_id=chat_id, text='💵⬇️ Введи минимальную цену за ночь $.')

    else:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_message(chat_id=chat_id, text='❕ Ответ должен быть числом от 1 до 10.')


@bot.message_handler(state=UserStates.price_range)
@logger.catch
def get_price_range(message: Message) -> None:
    """
    Хендлер, ожидающий минимальную и максимальную цены от пользователя.
    1. Проверяет записи в "data" о ценах,
    и соответствие сообщения к допустимому значению
    (максимальная цена не должна быть меньше минимальной).
    2. После добавления диапазона цен пользователем
    запрашивает максимальное расстояние до центра города.

    :param message: сообщение Телеграм.
    """
    user_price = message.text
    chat_id = message.chat.id
    message_id = message.message_id

    if user_price.isdigit() and int(user_price) >= 0:
        with bot.retrieve_data(chat_id, chat_id) as data:
            if not data.get('min_price'):
                data['min_price'] = user_price
                bot.delete_message(chat_id=chat_id, message_id=message_id)
                bot.send_message(chat_id=chat_id,
                                 text=f'✅ Цена от: {user_price}$.')
                bot.send_message(chat_id=chat_id, text='💵⬆️ Введи максимальную цену за ночь $.')
            else:
                if int(user_price) > int(data.get('min_price')):
                    data['max_price'] = user_price
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                    bot.send_message(chat_id=chat_id,
                                     text=f'✅ Цена до: {user_price}$.')
                    bot.set_state(user_id=message.from_user.id,
                                  state=UserStates.distance,
                                  chat_id=chat_id)
                    bot.send_message(chat_id=chat_id, text='📍 Введи максимальное расстояние до центра (км).')
                else:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                    bot.send_message(chat_id=chat_id,
                                     text=f'❕ Максимальная цена должна быть больше {data.get("min_price")}.')
    else:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_message(chat_id=chat_id, text='❕ Ответ должен быть положительным числом')


@bot.message_handler(state=UserStates.distance)
@logger.catch
def get_distance(message: Message) -> None:
    """
    Хендлер, ожидающий от пользователя максимальное расстояние до центра города.
    1. Проверяет, равно ли значение цифре больше нуля.
    2. Записывает значение в data['distance'].
    3. Отправляет сообщение с параметрами поиска и инициализирует функцию "output_hotels_info".

    :param message: сообщение Телеграм.
    """
    user_distance = message.text
    chat_id = message.chat.id
    message_id = message.message_id

    if user_distance.isdigit() and int(user_distance) > 0:
        with bot.retrieve_data(chat_id, chat_id) as data:
            data['distance'] = user_distance
            data_dict = deepcopy(data)

        bot.delete_message(chat_id=chat_id,
                           message_id=message_id)
        bot.send_message(chat_id=chat_id,
                         text=f'✅ Максимальное расстояние до центра: {user_distance} км.')

        params_text = search_params_output(data=data_dict)
        bot.send_message(chat_id=chat_id,
                         text=params_text)
        output_hotels_info(data=data_dict, message=message)

    else:
        bot.delete_message(chat_id=chat_id,
                           message_id=message_id)
        bot.send_message(chat_id=chat_id,
                         text='❕ Расстояние должно быть числом больше нуля.')
