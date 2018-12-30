import uuid

from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)
from django.db import models
from django.utils import timezone
from idolmaster.models import Idol

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(
        primary_key=True,
        unique=True,
        editable=False,
        default=uuid.uuid4,
        verbose_name='PK'
    )

    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        unique=True,
    )

    nickname = models.CharField(
        verbose_name='Nickname',
        max_length=30
    )

    is_active = models.BooleanField(
        verbose_name='Is active',
        default=True
    )
    date_joined = models.DateTimeField(
        verbose_name='Date joined',
        default=timezone.now
    )

    myIdol = models.ForeignKey(
        Idol,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    token = models.TextField(
        default=''
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', ]

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('-date_joined',)

    def __str__(self):
        return self.nickname

    def get_username(self):
        return self.nickname

    @property
    def is_staff(self):
        return self.is_superuser


class CameLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    info = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
