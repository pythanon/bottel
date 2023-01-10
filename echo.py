from loader import bot
from loguru import logger
from telebot.types import Message


@bot.message_handler(state=None)
@logger.catch
def bot_echo(message: Message) -> None:
    """
    Хендлер для захвата сообщений без состояния.

    :param message: сообщение Телеграм.
    """
    bot.reply_to(message, 'Я тебя не понимаю(\n'
                          'Попробуй команду /help')
