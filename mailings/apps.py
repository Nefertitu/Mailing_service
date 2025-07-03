import logging
import os

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger("mailings")


class MailingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mailings"
    _scheduler_started = False

    def ready(self) -> None:
        """Импорт сигналов"""

        from mailings import signals

        print(f"Сигналы загружены: {signals.__name__}")
        if not settings.DEBUG or os.environ.get("RUN_MAIN") and not self._scheduler_started:
            try:
                from .scheduler import start_scheduler

                start_scheduler()
                self._scheduler_started = True
                print("Старт планировщика")
                logger.info("Планировщик успешно инициализирован")
            except ImportError as e:
                logger.error(f"Ошибка инициализации: {e}")

    def _start_scheduler(self) -> None:
        """Запускает планировщик гарантированно один раз"""

        if not self._scheduler_started:
            try:
                from .scheduler import start_scheduler

                start_scheduler()
                self._scheduler_started = True
                logger.info("Планировщик рассылок успешно запущен")
            except Exception as e:
                logger.error(f"Ошибка запуска планировщика: {e}", exc_info=True)
