from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore[import-untyped]


class User(AbstractUser):
    """Модель пользователя с кастомными полями.
    Заменяет стандартный `username` на `email`
    в качестве основного идентификатора."""

    username = None  # type: ignore[assignment]
    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = PhoneNumberField(
        region="RU", blank=True, null=True, verbose_name="Телефон", help_text="Введите номер телефона"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар", help_text="Загрузите свой аватар"
    )
    COUNTRY_CHOICES = [
        ('RU', 'Russia'),
        ('KZ', 'Kazakhstan'),
        ('BY', 'Belarus'),
        ('US', 'United States'),
        ('DE', 'Germany'),
        ('UK', 'United Kingdom'),
        ('GE', 'Georgia'),
        ('OTHER', 'Other country')

    ]
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, blank=True, null=True)
    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        """Строковое представление объекта пользователя"""
        return self.email



