from loader import bot
from keyboards.inline.history_actions import make_history_action_kb
from database.db_sqlite import show_histories_list, clear_history
from loguru import logger
from telebot.types import Message, CallbackQuery


@bot.message_handler(commands=['history'])
@logger.catch
def history(message: Message) -> None:
    """
    Хендлер для команды "history".
    Собирает и показывает клавиатуру выбора действия с историей поиска.

    :param message: сообщение Телеграм.
    """
    kb = make_history_action_kb()
    bot.send_message(message.from_user.id, 'Что нужно сделать?', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == 'show_history')
@logger.catch
def show_history_handler(call: CallbackQuery) -> None:
    """
    Коллбек-хендлер для захвата кнопки с выбором действия "показать историю".
    Выполняет функцию "show_histories_list".

    :param call: отклик клавиатуры.
    """
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_histories_list(call.message, call.from_user.username)


@bot.callback_query_handler(func=lambda call: call.data == 'clear_history')
@logger.catch
def clear_history_handler(call: CallbackQuery) -> None:
    """
    Коллбек-хендлер для захвата кнопки с выбором действия "очистить историю".
    Выполняет функцию "clear_history".

    :param call: отклик клавиатуры.
    """
    bot.delete_message(call.message.chat.id, call.message.message_id)
    clear_history(call.message, call.from_user.username)
