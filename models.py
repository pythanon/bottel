from peewee import *
from loader import db


class BaseModel(Model):
    """
    Базовый класс для создания таблиц в БД и передачи ссылки на БД.
    """
    class Meta:
        database = db


class User(BaseModel):
    """
    Класс для создания таблицы с пользователями в БД.
    Родитель "BaseModel".

    Attributes:
        id: id пользователя в БД.
        name (str): имя пользователя Телеграм.
    """

    id = PrimaryKeyField(unique=True, null=False)
    name = CharField(unique=True, null=False)

    class Meta:
        db_table = 'Users'
        order_by = 'id'


class History(BaseModel):
    """
    Класс для создания таблицы с историей поисковых запросов в БД.
    Родитель "BaseModel".

    Attributes:
        from_user (str): имя пользователя из таблицы "Users".
        date (datetime.date): дата запроса.
        command (str): команда запроса.
        city (str): город запроса.
    """

    from_user = ForeignKeyField(User.name)
    date = DateField()
    command = CharField()
    city = CharField()

    class Meta:
        db_table = 'Histories'
        order_by = 'date'


class HotelInfo(BaseModel):
    """
    Класс для создания таблицы с результатами поисковых запросов в БД.
    Родитель "BaseModel".

    Attributes:
        from_date (datetime.date): дата запроса из таблицы "Histories".
        text (str): текст с информацией об отеле.

    """
    from_date = ForeignKeyField(History.date)
    text = CharField()

    class Meta:
        db_table = 'HotelsInfo'


