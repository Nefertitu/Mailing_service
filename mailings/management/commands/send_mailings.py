import logging
from typing import Any

from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from mailings.models import Mailing

logger = logging.getLogger("mailings")


class Command(BaseCommand):
    """Команда для отправки рассылки через интерфейс пользователя и командную строку"""

    help = "Тестовая рассылка"

    def handle(self, *args: Any, **options: Any) -> str | None:
        """Основной метод выполнения команды"""

        time_now = timezone.now()

        active_mailings = (
            Mailing.objects.filter(
                models.Q(start_at__lte=time_now, end_at__gte=time_now, status=Mailing.CREATED)
                | models.Q(status=Mailing.LAUNCHED, end_at__gte=time_now)
            )
            .select_related("message")
            .prefetch_related("recipients")
        )

        if not active_mailings.exists():
            self.stdout.write(self.style.WARNING("Нет активных рассылок для отправки"))
            return "no_active_mailings"
        self.stdout.write(f"Найдено {active_mailings.count()} активных рассылок:")

        for mailing in active_mailings:
            self.stdout.write(f"\n--- Рассылка по ID: {mailing.pk} ---")
            self.stdout.write(f"Тема: {mailing.message.title if mailing.message else 'Без темы'}")
            self.stdout.write(f"Получателей: {mailing.recipients.count()}")


            if not mailing.prepare_for_sending():
                self.stdout.write(self.style.WARNING("Рассылка уже завершена"))
                continue

            results = mailing.send_emails()

            errors: list[str] = []
            if isinstance(results["errors"], list):
                errors = results["errors"]
            elif isinstance(results["errors"], int) and results["errors"] > 0:
                errors = [f"{results['errors']} ошибок (детали в логах)"]

            self.stdout.write(self.style.SUCCESS(f"Успешно отправлено: {results['success']}/{results['total']}"))

            if errors:
                self.stdout.write(self.style.ERROR(f"Ошибки ({len(errors)}):"))
                for error in errors[:3]:
                    self.stdout.write(f"  • {error}")

                logger.error(f"Ошибки при отправке рассылки {mailing.pk}:")
                for error in errors:
                    logger.error(error)

        self.stdout.write(
            self.style.SUCCESS(f"\nОбработка завершена. Всего обработано рассылок: {active_mailings.count()}")
        )
        return "success"
