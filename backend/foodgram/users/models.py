from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        verbose_name='Логин пользователя',
    )
    email = models.EmailField(
        db_index=True,
        unique=True,
        verbose_name='Почтовый адрес',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
    )
    is_subscribed = models.BooleanField(
        db_index=True,
        default=False,
        verbose_name='Подписан ли текущий пользователь на этого',
    )

    REQUIRED_FIELDS = ['email', 'password', ]


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_subscribe(self):
        return self.is_subscribed
