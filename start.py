from telebot.types import Message
from loader import bot
from loguru import logger


@bot.message_handler(commands=['start'])
@logger.catch
def bot_start(message: Message) -> None:
    """
    Хендлер для команды "start".
    Ответом выводит сообщение с доступными командами бота.

    :param message: сообщение Телеграм.
    """
    bot.reply_to(message, f'👋 Привет, {message.from_user.first_name}!\n'
                          f'👇 Открой меню и посмотри, что я умею!')

