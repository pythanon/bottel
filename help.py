from config_data.config import DEFAULT_COMMANDS
from loader import bot
from loguru import logger
from telebot.types import Message


@bot.message_handler(commands=['help'])
@logger.catch
def bot_help(message: Message) -> None:
    """
    Хендлер для команды "help".
    Ответом выводит сообщение с доступными командами бота.

    :param message: сообщение Телеграм.
    """
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))
