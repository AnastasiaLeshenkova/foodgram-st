from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models 

class MeUser (AbstractUser):
    """ Модель пользователя """

    last_name = models.CharField(max_length=70, verbose_name='Имя пользователя')
    first_name = models.CharField(max_length=70, verbose_name='Фамилия пользователя')
    username = models.CharField(max_length=70, verbose_name='Ник`нейм пользователя', unique=True)
    email = models.EmailField(unique=True, verbose_name='Email пользователя')

    groups = models.ManyToManyField(
        Group,
        related_name='meuser_set', #####
        blank=True,
        verbose_name='Группы пользователя'
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='meuser_set',  ####
        blank=True,
        verbose_name='Разрешения пользователя'
    )

    def __str__(self):
        return self.username


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class MeFollow (models.Model):
    """ Модель подписок """

    user = models.ForeignKey(
        MeUser,
        on_delete=models.CASCADE,
        related_name='user_followers',
        verbose_name='Подписчик')

    author = models.ForeignKey(
        MeUser,
        on_delete=models.CASCADE,
        related_name='following_authors',
        verbose_name='Автор'
    )

    data = models.DateTimeField(auto_now=True, verbose_name='Дата подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Пользователь {self.user} подписан на автора {self.author}'

# Create your models here.
