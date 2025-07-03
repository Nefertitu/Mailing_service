from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from mailings.models import Mailing


class User(AbstractUser):
    """Модель пользователя с кастомными полями.
    Заменяет стандартный `username` на `email`
    в качестве основного идентификатора."""

    username = None  # type: ignore[assignment]
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Email пользователя",
    )
    phone_number = PhoneNumberField(
        region="RU", blank=True, null=True, verbose_name="Телефон", help_text="Введите номер телефона"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар", help_text="Загрузите свой аватар"
    )
    COUNTRY_CHOICES = [
        ("RU", "Russia"),
        ("KZ", "Kazakhstan"),
        ("BY", "Belarus"),
        ("US", "United States"),
        ("DE", "Germany"),
        ("UK", "United Kingdom"),
        ("GE", "Georgia"),
        ("OTHER", "Other country"),
    ]
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, blank=True, null=True)
    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)
    is_manager = models.BooleanField(
        default=False, null=True, blank=True, help_text="Добавление пользователю статуса 'менеджер'"
    )
    is_active = models.BooleanField(
        verbose_name="",
        default=True,
        help_text="✅Активен/◻️Неактивен (Снять отметку, сделав пользователя неактивным)",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        """Строковое представление объекта пользователя"""
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

        permissions = [
            ("can_block_users", "Can block users"),
        ]

    def can_view_recipients(self, mailing: "Mailing") -> bool:
        """Проверяет, имеет ли пользователь право просматривать получателей рассылки"""

        return self.is_manager or mailing.owner == self
