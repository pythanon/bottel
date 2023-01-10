from telebot.handler_backends import State, StatesGroup


class UserStates(StatesGroup):
    """
    Класс для реализации состояний пользователя внутри сценария.
    Родитель: StatesGroup

    Attributes:
        command: команда пользователя
        cities_dict: список предложенных городов для уточнения
        hotels_amount: кол-во отелей для вывода
        need_photo: необходимость вывода фото
        photo_amount: кол-во фото для вывода
        price_range: диапазон цен отелей за ночь
        distance: максимальное расстояние до центра города
    """
    command = State()
    cities_dict = State()
    hotels_amount = State()
    need_photo = State()
    photo_amount = State()
    price_range = State()
    distance = State()

