from loader import bot
from states.user_states import UserStates
from handlers import get_info_handlers
from loguru import logger
from telebot.types import Message


@bot.message_handler(commands=['lowprice'])
@logger.catch
def low_price(message: Message) -> None:
    """
    Хендлер для команды 'lowprice'.
    1. Устанавливает состояние "cities_dict".
    2. Запрашивает город у пользователя.
    3. Сохраняет команду и тип сортировки в "data"

    :param message: сообщение Телеграм
    """
    bot.set_state(message.from_user.id, UserStates.cities_dict, message.chat.id)
    bot.send_message(message.from_user.id, '🏙 В каком городе будем искать?')

    with bot.retrieve_data(message.chat.id, message.chat.id) as data:
        data['command'] = 'lowprice'
        data['sort_type'] = 'PRICE_LOW_TO_HIGH'
