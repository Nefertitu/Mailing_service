from django.db import models
from django.utils import timezone

from user.models import User


class Recipient(models.Model):
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
        return self.email

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
        return f"Тема: '{self.title}'"

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = ["title"]


class Mailing(models.Model):
    """Модель рассылки"""

    CREATED = "Создана"
    LAUNCHED = "Запущена"
    COMPLETED = "Завершена"

    STATUS_CHOICES = [
        (CREATED, "Создана"),
        (LAUNCHED, "Запущена"),
        (COMPLETED, "Завершена"),
    ]

    start_at = models.DateTimeField(
        verbose_name="Дата и время первой отправки",
        help_text="Введите дату и время в формате: 'гггг-мм-дд чч-мм'",
    )
    end_at = models.DateTimeField(
        verbose_name="Дата и время окончания отправки",
        blank=True,
        null=True,
        help_text="Необязательно. Если указано, рассылка прекратится после этой даты."
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        verbose_name="Статус рассылки",
        default=CREATED,
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        null=False,
        related_name="mailings",
    )
    recipients = models.ManyToManyField(
        "Recipient",
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

    def __str__(self) -> str:
        """Строковое отображение рассылки"""
        return f"Рассылка сообщения '{self.message.title}' (старт: {self.start_at}, завершение: {self.end_at})"

    class Meta:
        ordering = ["start_at", "end_at"]

    def get_recipients_display(self):
        return ", ".join([recipient.email for recipient in self.recipients.all()])

    def get_message_title(self):
        """Оптимизированная версия без лишних проверок"""
        return self.message.title

    def send_emails(self):
        """Отправка писем и ручной переход в LAUNCHED"""
        if self.status == self.CREATED:
            self.status = self.LAUNCHED
            self.start_at = timezone.now()
            self.save()

    def update_status(self):
        """Автоматическое обновление статуса рассылки"""
        now = timezone.now()

        if self.status == self.LAUNCHED and self.end_at and self.end_at <= now:
            self.status = self.COMPLETED
            self.save()


class MailingAttempt(models.Model):
    """Модель попытка рассылки"""

    SUCCESSFULLY = "Успешно"
    UNSUCCESSFUL = "Не успешно"

    ATTEMPT_CHOICES = [
        (SUCCESSFULLY, "Успешно"),
        (UNSUCCESSFUL, "Не успешно"),
    ]

    datetime_attempt = models.DateTimeField(
        verbose_name="Дата и время попытки",
       auto_now_add=True,
    )
    status = models.CharField(
        max_length=50,
        choices=ATTEMPT_CHOICES,
        verbose_name="Статус рассылки",
        default=None,
    )
    server_response = models.TextField(
        verbose_name="Ответ почтового сервера",
        blank=True,
        null=True,
        help_text="Ответ почтового сервера на отправку"
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        null=False,
        related_name="attempts",
        verbose_name="Рассылка",
        help_text="Связанная рассылка"
    )

    def __str__(self)  -> str:
        """Строковое отображение попытки рассылки"""
        return f"Попытка рассылки #{self.pk} ({self.mailing.message.title})"

    class Meta:
        ordering = ["datetime_attempt"]

    def get_message_title(self):
        """Возвращает строку с темой сообщения"""
        return self.mailing.message.title

