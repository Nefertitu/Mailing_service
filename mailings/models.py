import logging
import os
from datetime import timedelta, datetime
from typing import Any, Optional, Dict, Union, List, cast

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.http import HttpRequest
from django.utils import timezone
from mypy.dmypy.client import request

from user.models import User

logger = logging.getLogger("mailings")


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
        User, on_delete=models.CASCADE, related_name="recipients", help_text="Владелец(Пользователь)"
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

    @staticmethod
    def get_recipients_display(user: Optional["User"] = None) -> str:
        """Возвращает отформатированную строку получателей с учетом прав доступа"""

        recipients = Recipient.objects.all()

        if user and not user.is_manager:
            recipients = recipients.filter(owner=user)
        recipients = recipients

        return ", ".join(recipients.values_list("email", flat=True))


class Message(models.Model):
    """Модель сообщения"""

    title = models.CharField(
        max_length=200,
        verbose_name="Тема сообщения",
        help_text="Введите тему письма",
    )
    body = models.TextField(
        verbose_name="Тело письма",
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_messages", help_text="Владелец(Пользователь)"
    )

    def __str__(self) -> str:
        """Строковое отображение сообщения"""
        return f"Тема: '{self.title}'"

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = ["title"]

    @staticmethod
    def get_messages_display(user: Optional["User"] = None) -> str:
        """Возвращает отформатированную строку получателей с учетом прав доступа"""

        messages = Message.objects.all()

        if user and not user.is_manager:
            messages = messages.filter(owner=user)
        messages = messages

        return ", ".join(messages.values_list("title", flat=True))


class Mailing(models.Model):
    """Модель рассылки"""

    CREATED = "Создана"
    LAUNCHED = "Запущена"
    COMPLETED = "Завершена"

    DAILY = "Ежедневно"
    WEEKLY = "Еженедельно"
    MONTHLY = "Ежемесячно"

    STATUS_CHOICES = [
        (CREATED, "Создана"),
        (LAUNCHED, "Запущена"),
        (COMPLETED, "Завершена"),
    ]

    start_at = models.DateTimeField(
        verbose_name="Дата и время первой отправки",
        help_text="Выберите дату и время начала рассылки",
    )
    end_at = models.DateTimeField(
        verbose_name="Дата и время окончания отправки",
        blank=True,
        null=True,
        help_text="Выберите дату и время завершения рассылки",
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
        Recipient,
        related_name="received_mailings",
        symmetrical=False,
        verbose_name="Получатели рассылки",
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_mailings", help_text="Владелец(Пользователь)"
    )
    is_periodic = models.BooleanField(
        default=False,
        verbose_name="Периодическая рассылка",
        null=True,
        blank=True,
    )
    PERIOD_CHOICES = [
        ("DAILY", "Ежедневно"),
        ("WEEKLY", "Еженедельно"),
        ("MONTHLY", "Ежемесячно"),
    ]
    period = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        blank=True,
        null=True,
    )
    next_run = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Следующий запуск",
    )
    is_active = models.BooleanField(
        verbose_name="Рассылка активна ('Да/Нет')",
        default=True,
        null=True,
        blank=True,
        help_text="Отключение рассылки. Выберите нужный вариант",
    )

    def __str__(self) -> str:
        """Строковое отображение рассылки"""
        return (
            f"Рассылка сообщения '{self.message.title}': ({'Периодическая' if self.is_periodic else 'Одномоментная'})"
        )

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        ordering = ["start_at", "end_at", "is_periodic"]

        permissions = [
            ("can_disable_mailings", "Can disable mailings"),
        ]

    def get_recipients_display(self) -> str:
        """Возвращает строку с 'email' получателей текущей рассылки"""

        emails = self.recipients.values_list("email", flat=True)
        return ", ".join(emails)

    def get_message_title(self) -> str:
        """Возвращает заголовок сообщения"""
        return self.message.title

    def prepare_for_sending(self) -> bool:
        """Подготовка рассылки к отправке (обновление статуса)"""

        now = timezone.now()

        if self.status == self.COMPLETED:
            return False

        if self.end_at and self.end_at <= now:
            self.status = self.COMPLETED
            logger.info(f"Рассылка {self.pk} переведена в статус 'Завершена'")
            self.save()
            return False

        if self.status == self.CREATED:
            self.status = self.LAUNCHED
            logger.info(f"Рассылка {self.pk} переведена в статус 'Запущена'")
            self.start_at = timezone.now()
            self.save()

        return True

    def send_emails(self) -> Dict[str, Union[int, List[str]]]:
        """Отправка писем"""

        results: Dict[str, Union[int, List[str]]] = {
            "total": self.recipients.count(),
            "success": 0,    # int
            "errors": [],    # List[str]
        }
        recipients = self.recipients.all()
        message = self.message

        print(f"DEBUG: Отправка для рассылки {self.pk}")
        logger.info(f"Начало отправки для {self.pk}")
        for recipient in recipients:
            logger.info(f"Отправка для {recipient.email}")
            try:
                send_mail(
                    subject=message.title,
                    message=message.body,
                    from_email=os.getenv("EMAIL_HOST_USER"),
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                logger.info(f"Успешно отправлено письмо на {recipient.email}")
                MailingAttempt.objects.create(
                    mailing=self,
                    status=MailingAttempt.SUCCESSFULLY,
                    server_response=f"Успешно отправлено: {recipient.email}",
                )
                success = results["success"]
                if isinstance(success, int):
                    success += 1
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=self,
                    status=MailingAttempt.UNSUCCESSFUL,
                    server_response=f"Ошибка при отправке {recipient.email}: {str(e)}",
                )
                logger.error(f"Ошибка отправки: {str(e)}", exc_info=True)
                errors = results["errors"]
                if isinstance(errors, list):
                    errors.append(str(e))
                raise

        return results

    def send(self) -> bool:
        """Основной метод отправки"""

        if not self.prepare_for_sending():
            logger.warning("Нет активных рассылок для отправки")
            return False

        self.send_emails()
        self.update_status()
        return True

    def update_status(self) -> bool:
        """Автоматическое обновление статуса рассылки"""

        now = timezone.now()

        if not self.is_periodic:
            if self.end_at and self.end_at <= now:
                self.status = self.COMPLETED
                self.is_active = False
                return True
            return False

        if self.next_run is not None and self.next_run <= now:
            self.schedule_next_run()
            return True

        end_at = cast(Optional[datetime], self.end_at)
        if (self.is_periodic
                and end_at
                and end_at <= now
                and self.status != self.COMPLETED):
            self.status = self.COMPLETED
            self.is_active = False
            return True

        return False

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Переопределённый метод сохранения с проверкой статуса"""

        # old_status = self.status
        # now = timezone.now()
        #
        # if self.end_at and self.end_at <= now:
        #     self.status = self.COMPLETED
        #     self.is_active = False
        #     status_updated = True
        # else:
        #     status_updated = self.update_status()
        # if status_updated:
        #     print(f"Статус рассылки {self.pk} изменён: {old_status} → {self.status}")
        #     kwargs['update_fields'] = ['status', 'is_active', *kwargs.get('update_fields', [])]
        #     kwargs['force_update'] = True
        self.update_status()
        super().save(*args, **kwargs)

        # if status_updated:
        #     from .services import clear_mailing_cache
        #     clear_mailing_cache()

    def clean(self) -> None:
        """Валидация перед сохранением"""
        if self.is_periodic and not self.period:
            raise ValidationError("Для периодической рассылки должен быть указан период")

    def schedule_next_run(self) -> None:
        """Вычисление следующего времени запуска для периодических рассылок"""

        if self.is_periodic and self.period:
            now = timezone.now()
            if self.period == "DAILY":
                self.next_run = now + timedelta(days=1)
            elif self.period == "WEEKLY":
                self.next_run = now + timedelta(weeks=1)
            elif self.period == "MONTHLY":
                self.next_run = now + timedelta(days=30)
            self.save()

    def get_periodic_display(self) -> str:
        """Отображение информации о рассылке"""
        return "Рассылка по расписанию" if self.is_periodic else ""

    def get_custom_period_display(self) -> str:    # type: ignore[empty-body]
        """Отображение информации о периоде рассылки"""

        if not self.period:
            return ""
        return dict(self.PERIOD_CHOICES).get(self.period, self.period or "")

    @property
    def schedule_details(self) -> Dict[str, Any]:
        """Возвращает детализированную информацию о расписании в виде словаря"""

        result: Dict[str, Any]  = {
            "is_periodic": self.is_periodic,
            "period": None,
            "next_run": None
        }

        if self.is_periodic:
            result.update({
                "period": self.get_custom_period_display() if self.period else None,
                "next_run": self.next_run.strftime("%d.%m.%Y %H:%M") if self.next_run else None,
            })
        return result


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
        verbose_name="Ответ почтового сервера", blank=True, null=True, help_text="Ответ почтового сервера на отправку"
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        null=False,
        related_name="attempts",
        verbose_name="Рассылка",
        help_text="Связанная рассылка",
    )

    def __str__(self) -> str:
        """Строковое отображение попытки рассылки"""
        return f"Попытка рассылки #{self.pk} ({self.mailing.message.title})"

    class Meta:
        verbose_name = "попытка рассылки"
        verbose_name_plural = "попытки рассылок"
        ordering = ["datetime_attempt"]

    def get_message_title(self) -> str:
        """Возвращает строку с темой сообщения"""
        return self.mailing.message.title
