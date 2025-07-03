from typing import Optional

from django.core.cache import cache
from django.db.models import QuerySet, Prefetch
from django.utils import timezone

from config.settings import CACHE_ENABLED
from user.models import User

from .models import Mailing, MailingAttempt, Message, Recipient


class StatisticsService:
    """Сервис для работы с отчетными данными пользователей с разными правами доступа"""

    @staticmethod
    def get_user_stats(user: User) -> dict:
        """Метод для получения отчетных данных для пользователя с правами 'owner'"""

        user_mailings = Mailing.objects.filter(owner=user)
        return {
            "attempts_all": MailingAttempt.objects.filter(mailing__in=user_mailings).count(),
            "attempts_successfully": MailingAttempt.objects.filter(
                mailing__in=user_mailings, status=MailingAttempt.SUCCESSFULLY
            ).count(),
            "recipients_all": Recipient.objects.filter(owner=user).count(),
            "messages_all": Message.objects.filter(owner=user).count(),
            "datetime_now": timezone.now(),
        }

    @staticmethod
    def get_manager_stats() -> dict:
        """Метод для получения отчетных данных для пользователя с правами доступа 'is_manager'"""

        return {
            "attempts_all": MailingAttempt.objects.count(),
            "attempts_successfully": (MailingAttempt.objects.filter(status=MailingAttempt.SUCCESSFULLY)).count(),
            "recipients_all": Recipient.objects.all().count(),
            "messages_all": Message.objects.all().count(),
            "datetime_now": timezone.now(),
        }

class DataService:
    """Сервис для работы с данными пользователей"""

    def get_recipients_from_cache(self,  user: "Optional[User]" = None) -> QuerySet[Recipient]:
        """Получает данные о клиентах из кэша, если кэш пуст,
        получает данные из базы данных"""

        if not CACHE_ENABLED:
            print("Кэш отключен")
            if user.is_manager:
                return Recipient.objects.all()
            return Recipient.objects.filter(owner=user)

        if user is None or user.is_manager:
            key = "recipients_list_all"
        else:
            key = f"recipients_list_{user.pk}"

        recipients = cache.get(key)
        print(f"Попытка получить по ключу: {key}")

        if recipients is not None:
            print(f"Данные найдены в кэше: {key}")
            return recipients
        print("Данные не найдены в кэше, запрос к БД")

        if user is None or user.is_manager:
            recipients = Recipient.objects.all()
        else:
            recipients = Recipient.objects.filter(owner=user)

        cache.set(key, recipients)
        print(f'Данные сохранены в кэше по ключу: {key}')
        return recipients


    def get_messages_from_cache(self, user: "Optional[User]" = None) -> QuerySet[Message]:
        """Получает данные о клиентах из кэша, если кэш пуст,
        получает данные из базы данных"""

        if not CACHE_ENABLED:
            print("Кэш отключен")
            if user:
                return Message.objects.filter(owner=user)

        if user is None:
            key = "messages_list_all"
        else:
            key = f"messages_list_{user.pk}"

        messages = cache.get(key)
        print(f"Попытка получить по ключу: {key}")

        if messages is not None:
            print(f"Данные найдены в кэше: {key}")
            return messages
        print("Данные не найдены в кэше, запрос к БД")

        if user is None:
            messages = Message.objects.all()
        else:
            messages = Message.objects.filter(owner=user)

        cache.set(key, messages)
        print(f'Данные сохранены в кэше по ключу: {key}')
        return messages


    def get_mailings_from_cache(self, user: "Optional[User]" = None) -> QuerySet[Mailing]:
        """Получает данные о клиентах из кэша, если кэш пуст,
        получает данные из базы данных"""

        if not CACHE_ENABLED:
            print("Кэш отключен")
            if user.is_manager:
                qs = Mailing.objects.all()
            qs = Mailing.objects.filter(owner=user)
            return self._update_mailings_status(qs)

        if user is None or user.is_manager:
            key = "mailings_list_all"
        else:
            key = f"mailing_list_{user.pk}"

        mailings = cache.get(key)
        print(f"Попытка получить по ключу: {key}")

        if mailings is not None:
            print(f"Данные найдены в кэше: {key}")
            return self._update_mailings_status(mailings)
        print("Данные не найдены в кэше, запрос к БД")

        if user is None or user.is_manager:
            mailings = mailings = Mailing.objects.select_related(
                'message', 'owner'
                ).prefetch_related(
                Prefetch(
                    'recipients',
                    queryset=Recipient.objects.only('email', 'owner__id', 'owner__email')
                )).all()
        else:
            mailings = Mailing.objects.filter(owner=user).select_related(
                'message', 'owner'
                ).prefetch_related(
                Prefetch(
                    'recipients',
                    queryset=Recipient.objects.only('email', 'owner__id', 'owner__email'),
                    to_attr='prefetched_emails'
                )
            ).only(
                'id',
                'message__id',
                'status',
                'owner__id'
            )

        cache.set(key, mailings)
        print(f'Данные сохранены в кэше по ключу: {key}')
        return self._update_mailings_status(mailings)

    def _update_mailings_status(self, mailings: QuerySet[Mailing]) -> QuerySet[Mailing]:
        """Внутренний метод для обновления статусов рассылок"""
        now = timezone.now()

        to_update = []
        for mailing in mailings:
            if mailing.end_at and mailing.end_at <= now and mailing.status != Mailing.COMPLETED:
                mailing.status = Mailing.COMPLETED
                mailing.is_active = False
                to_update.append(mailing)

        if to_update:
            Mailing.objects.bulk_update(
                to_update,
                ['status', 'is_active'],
                batch_size=100
            )

        return mailings


    # def get_users_from_cache(self, user: "Optional[User]") -> QuerySet[User, User] | None | Any:
    #     """Получает данные о клиентах из кэша, если кэш пуст,
    #     получает данные из базы данных"""
    #
    #     if not CACHE_ENABLED:
    #         print("Кэш отключен")
    #         if user.is_manager:
    #             return User.objects.all()
    #
    #     if user.is_manager:
    #         key = "users_list_all"
    #
    #         users = cache.get(key)
    #         print(f"Попытка получить по ключу: {key}")
    #
    #         if users is not None:
    #             print(f"Данные найдены в кэше: {key}")
    #             return users
    #         print("Данные не найдены в кэше, запрос к БД")
    #
    #         if user.is_manager:
    #             users = User.objects.all()
    #
    #         cache.set(key, users)
    #         print(f'Данные сохранены в кэше по ключу: {key}')
    #         return users


