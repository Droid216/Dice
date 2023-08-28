from django.contrib.auth.models import AbstractUser, User
from django.db import models


class City(models.Model):
    city = models.CharField(max_length=20, unique=True, verbose_name="Город")
    close = models.BooleanField(default=False, db_index=True, verbose_name="Нет филиалов")

    objects = models.Manager()

    def __str__(self):
        return self.city

    class Meta:
        ordering = ['city']
        verbose_name = 'город'
        verbose_name_plural = 'города'


class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name="Город")
    address = models.CharField(max_length=30, verbose_name="Адрес")
    close = models.BooleanField(default=False, db_index=True, verbose_name="Закрыто")

    objects = models.Manager()

    def __str__(self):
        return self.address

    class Meta:
        ordering = ['city', 'address']
        verbose_name = 'адрес'
        verbose_name_plural = 'адреса'


class Room(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="Название")
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name="Город")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, verbose_name="Адрес")
    photo = models.ImageField(upload_to='room/photo', verbose_name="Фото")
    icon = models.ImageField(upload_to='room/icon', blank=True, null=True, verbose_name="Иконка")
    close = models.BooleanField(default=False, db_index=True, verbose_name="Закрыта")

    objects = models.Manager()

    def __str__(self):
        return str(self.name) + "(" + str(self.address) + ")"

    class Meta:
        ordering = ['city', 'address', 'name']
        verbose_name = 'комната'
        verbose_name_plural = 'комнаты'


class Systems(models.Model):
    CHOICE_DIFFICULTY_LEVEL = [
        ('1', 'Очень легко'),
        ('2', 'Легко'),
        ('3', 'Средне'),
        ('4', 'Сложно'),
        ('5', 'Очень сложно')
    ]
    system = models.CharField(max_length=30, verbose_name="Название")
    description = models.TextField(max_length=1000, verbose_name="Описание")
    image = models.ImageField(upload_to='systems/image', verbose_name="Изображение")
    icon = models.ImageField(upload_to='systems/icon', blank=True, null=True, verbose_name="Иконка")
    difficulty_level = models.CharField(max_length=1, choices=CHOICE_DIFFICULTY_LEVEL, default='1',
                                        verbose_name="Сложность")

    objects = models.Manager()

    def __str__(self):
        return self.system

    class Meta:
        ordering = ['system']
        verbose_name = 'система'
        verbose_name_plural = 'системы'


class Master(models.Model):
    name = models.CharField(max_length=20, verbose_name="Имя")
    last_name = models.CharField(max_length=20, verbose_name="Фамилия")
    description = models.TextField(max_length=1000, verbose_name="Описание")
    photo = models.ImageField(upload_to='master/photo', verbose_name="Фото")
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name="Город")
    on_holiday = models.BooleanField(default=False, db_index=True, verbose_name="В отпуске")
    fired = models.BooleanField(default=False, db_index=True, verbose_name="Уволен")

    objects = models.Manager()

    def __str__(self):
        return str(self.name) + " " + str(self.last_name)

    class Meta:
        ordering = ['name', 'last_name']
        verbose_name = 'мастер'
        verbose_name_plural = 'мастера'


class Game(models.Model):
    name = models.CharField(max_length=40, verbose_name="Название")
    system = models.ForeignKey(Systems, on_delete=models.PROTECT, verbose_name="Система")
    type_game = models.CharField(max_length=20, default="Ваншот", verbose_name="Тип сессии")
    description = models.TextField(max_length=900, verbose_name="Описание")
    image = models.ImageField(upload_to='game/image', verbose_name="Изображение")
    price = models.IntegerField(default=5000, verbose_name="Стоимость")
    master = models.ForeignKey(Master, on_delete=models.PROTECT, verbose_name="Мастер")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, verbose_name="Место игры")
    date = models.DateField(verbose_name="Дата проведения")
    time = models.TimeField(verbose_name="Время проведения")
    total_seats = models.IntegerField(default=6, verbose_name="Количество участников")
    filled_seats = models.IntegerField(default=0, verbose_name="Занято мест")
    canceled = models.BooleanField(default=False, db_index=True, verbose_name="Отменено")

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['date', 'time', 'room']
        verbose_name = 'игра'
        verbose_name_plural = 'игры'

User._meta.get_field('email')._unique = True


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    male = models.CharField(max_length=20, blank=True, null=True, choices=[('М', 'мужской'), ('Ж', 'женский')],
                            verbose_name='Пол')
    city = models.CharField(max_length=20, blank=True, null=True, verbose_name='Город')
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='Телефон')
    telegram = models.CharField(max_length=32, blank=True, null=True, verbose_name='Телеграм')
    birthday = models.DateField(verbose_name="Дата рождения", blank=True, null=True)
    avatars = models.ImageField(upload_to='user/avatars', default='user/avatars/user.png')

    objects = models.Manager()

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['user']
        verbose_name = 'игрок'
        verbose_name_plural = 'игроки'