from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger
from peewee import SqliteDatabase


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
logger.add('debug.log', format="{time}, {level}, {message}", level="DEBUG", rotation="10 MB", compression="zip")
db = SqliteDatabase('user_history.db')

