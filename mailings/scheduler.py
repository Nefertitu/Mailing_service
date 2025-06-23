import logging

from datetime import timedelta

from apscheduler.jobstores.base import ConflictingIdError
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from .models import Mailing


logger = logging.getLogger("mailings")


def check_periodic_mailings():
    """Проверка и запуск периодических рассылок"""

    if not hasattr(check_periodic_mailings, '_last_run'):
        check_periodic_mailings._last_run = timezone.now() - timedelta(minutes=10)

    now = timezone.now()
    print(f"\n=== DEBUG TIME: {now} ===")
    time_since_last_run = (now - check_periodic_mailings._last_run).total_seconds()

    if time_since_last_run < 300:
        logger.debug(f"Пропуск запуска. С момента последнего запуска прошло только {time_since_last_run:.1f} сек.")
        return

    check_periodic_mailings._last_run = now
    logger.info("==== Начало проверки рассылок ====")

    mailings = Mailing.objects.filter(
        is_periodic=True,
        start_at__lte=now,
        end_at__gte=now,
        status__in=[Mailing.CREATED, Mailing.LAUNCHED]
    ).select_related('message').prefetch_related('recipients')

    logger.info(f"Найдено рассылок: {mailings.count()}")
    for mailing in mailings:
        logger.info(f"Обработка рассылки ID={mailing.pk}, тема: '{mailing.message.title}'")
        try:
            result = mailing.send_emails()
            mailing.schedule_next_run()
            mailing.save()
            logger.info(f"Результат: {result['success']}/{result['total']} отправлено")
        except Exception as e:
            logger.error(f"Ошибка в рассылке {mailing.pk}: {str(e)}", exc_info=True)


def start_scheduler():
    """Запуск планировщика"""

    if hasattr(start_scheduler, '_executed'):
        return

    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    try:
        scheduler.add_job(
            check_periodic_mailings,
            "cron",
            minute="*/5",
            id="periodic_mailings_check",
            replace_existing=True,
            max_instances=1
        )
    except ConflictingIdError:
        logger.warning("Задание уже существует, заменяем его")
        scheduler.add_job(
            check_periodic_mailings,
            'cron',
            minute="*/5",
            id='periodic_mailings_check',
            replace_existing=True,
            max_instances=1
        )

    try:
        logger.info("Запуск планировщика...")
        scheduler.start()
        start_scheduler._executed = True
    except KeyboardInterrupt:
        logger.info("Остановка планировщика...")
        scheduler.shutdown()
        logger.info("Рассылка по расписанию успешно завершена!")

    logger.info(f"Следующий запуск задачи: {scheduler.get_job('periodic_mailings_check').next_run_time}")