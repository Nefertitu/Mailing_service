from django.db import models

from user.models import User


class MailingRecipient(models.Model):
    """Модель получателя рассылки"""

    email = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Получатель рассылки",
        help_text="Введите email получателя рассылки",
    )
    fullname = models.CharField(
        max_length=200,
        verbose_name="Ф.И.О. получателя рассылки",
        help_text="Введите Ф.И.О получателя рассылки",
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipients",
        help_text="Владелец(Пользователь)"
    )
    comment = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True,
    )

    def __str__(self):
        """Строковое отображение получателя рассылки"""
        return f"Получатель рассылки: {self.email}"

    class Meta:
        verbose_name = "получатель"
        verbose_name_plural = "получатели"
        ordering = ["email"]

