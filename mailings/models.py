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

    def __str__(self) -> str:
        """Строковое отображение получателя рассылки"""
        return f"Получатель рассылки: {self.email}"

    class Meta:
        verbose_name = "получатель"
        verbose_name_plural = "получатели"
        ordering = ["email"]


class Message(models.Model):
    """Модель сообщения"""

    title = models.CharField(
        max_length=200,
        verbose_name="Тема письма",
        help_text="Введите тему письма",
    )
    body = models.TextField(
        verbose_name="Тело письма",
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Владелец(Пользователь)"
    )

    def __str__(self) -> str:
        """Строковое отображение сообщения"""
        return f"Тема сообщения: '{self.title}'"

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = ["title"]


class Mailing(models.Model):
    """Модель рассылки"""

    CREATED = "Создана"
    LAUNCHED = "Запущена"
    COMPLETED = "Завершена"

    MAILING_CHOICES = [
        (CREATED, "Создана"),
        (LAUNCHED, "Запущена"),
        (COMPLETED, "Завершена"),
    ]

    start_at = models.DateTimeField(
        verbose_name="Дата и время первой отправки",
        help_text="Дата и время начала отправки рассылки"
    )
    end_at = models.DateTimeField(
        verbose_name="Дата и время окончания отправки",
        blank=True,
        null=True,
        help_text="Необязательно. Если указано, рассылка прекратится после этой даты."
    )
    status = models.CharField(
        max_length=50,
        choices=MAILING_CHOICES,
        verbose_name="Статус рассылки",
        default=CREATED,
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailings",
    )
    recipients = models.ManyToManyField(
        "MailingRecipient",
        related_name="received_mailings",
        symmetrical=False,
        verbose_name="Получатели рассылки",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_mailings",
        help_text="Владелец(Пользователь)"
    )

    def __str__(self):
        message = Message.objects.get(self)
        message_title = message.title
        return f"Рассылка сообщения '{message_title}' (старт: {self.start_at}, завершение: {self.end_at})"

    class Meta:
        ordering = ["owner", "start_at", "end_at"]


