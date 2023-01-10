from datetime import datetime
from loader import bot
from loguru import logger
from database.models import db, User, History, HotelInfo
from keyboards.inline.history_list import output_histories
from telebot.types import Message, CallbackQuery


@logger.catch
def save_user_to_db(username: str) -> None:
    """
    Функция для избежания повторного добавления пользователя в БД.
    1. Проверяет наличие пользователя.
    2. Добавляет пользователя в БД.
    :param username: имя пользователя Телеграм.
    """
    with db:
        db.create_tables([User, History, HotelInfo])
        try:
            user_id = User.get(User.name == username)
        except Exception:
            user_id = None
        if not user_id:
            User(name=username).save()


@logger.catch
def save_history_to_db(username: str, command: str, city: str, hotels_list: list) -> None:
    """
    Функция для сохранения истории поиска в БД.

    :param username: имя пользователя Телеграм.
    :param command: команда поиска.
    :param city: город поиска.
    :param hotels_list: список результатов поиска.
    """
    with db:
        date = datetime.timestamp(datetime.now())
        History(from_user=username,
                date=date,
                command=command,
                city=city).save()
        time = History.select().where(History.from_user == username and History.date == date)
        for i_hotel_text in hotels_list:
            HotelInfo(from_date=time,
                      text=i_hotel_text).save()


@logger.catch
def show_histories_list(message: Message, username: str) -> None:
    """
    Функция для вывода истории поиска из БД.
    1. Собирает список истории поиска.
    2. Если список пустой, выводит соответствующее сообщение.
    3. Если в списке есть запросы, выводит инлайн клавиатуру с выбором конкретного запроса.

    :param message: сообщение Телеграм.
    :param username: имя пользователя Телеграм.
    """
    with db:
        histories_list = [history for history
                          in History.select().where(History.from_user == username)]
        if histories_list:
            kb = output_histories(histories_list)
            bot.send_message(chat_id=message.chat.id,
                             text='Выбери запрос 👇',
                             reply_markup=kb)
        else:
            bot.send_message(chat_id=message.chat.id,
                             text='📂 В истории пока что ничего нет.\n'
                                  '👉 Воспользуйся командой /help и посмотри, что еще можно сделать.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('history-'))
@logger.catch
def output_history_results(call: CallbackQuery) -> None:
    """
    Хендлер для захвата нажатия кнопки с выбором конкретного запроса в истории.
    1. Проходит циклом по выбранному запросу в БД.
    2. Отправляет результат в чат.

    :param call: отклик клавиатуры.
    """
    bot.delete_message(call.message.chat.id, call.message.message_id)
    history_date = int(call.data.replace('history-', ''))
    with db:
        for result in HotelInfo.select().where(HotelInfo.from_date == history_date):
            bot.send_message(chat_id=call.message.chat.id,
                             text=result.text,
                             parse_mode='html')
        bot.send_message(chat_id=call.message.chat.id,
                         text='🙃 Вывел все запросы!\n'
                              '👉 Воспользуйся командой /help и посмотри, что еще можно сделать.',
                         parse_mode='html')


@logger.catch
def clear_history(message: Message, username: str) -> None:
    """
    Функция для очистки истории поиска пользователя в БД.

    :param message: сообщение Телеграм.
    :param username: имя пользователя Телеграм.
    """
    with db:
        for history in History.select().where(History.from_user == username):
            history_date = History.get(History.date == history.date)
            HotelInfo.delete().where(HotelInfo.from_date == history_date).execute()
            History.delete_instance(history)
    bot.send_message(chat_id=message.chat.id,
                     text=f'✅ История очищена!\n'
                          f'👉 Воспользуйся командой /help и посмотри, что еще можно сделать.')
