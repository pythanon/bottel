import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести возможные команды бота"),
    ('lowprice', "Найти топ самых дешёвых отелей в городе"),
    ('highprice', "Найти топ самых дорогих отелей в городе"),
    ('bestdeal', "Найти отели по цене и расстоянию от центра"),
    ('history', "Вывести историю поиска")
)

RAPID_API_KEY = os.getenv('RAPID_API_KEY')

headers = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": 'hotels4.p.rapidapi.com'
}

payload = {'currency': 'USD',
           'eapid': 1,
           'locale': 'en_US',
           'siteId': 300000001,
           'destination': {
               'regionId': None
           },
           'checkInDate': {'day': None, 'month': None, 'year': None},
           'checkOutDate': {'day': None, 'month': None, 'year': None},
           'rooms': [{'adults': 1}],
           'resultsStartingIndex': 0,
           'resultsSize': 1000,
           'sort': None,
           'filters': {'availableFilter': 'SHOW_AVAILABLE_ONLY',
                       "price": {"max": None,
                                 "min": None
                                 }
                       }
           }

payload_for_details = {
    "currency": "USD",
    "eapid": 1,
    "locale": "en_US",
    "siteId": 300000001,
    "propertyId": None
}

