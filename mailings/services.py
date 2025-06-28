from django.db.models import QuerySet
from django.utils import timezone

from mailings.models import Mailing, MailingAttempt, Recipient, Message


class StatisticsService:
    """Сервис для работы с отчетными данными пользователей с разными правами доступа"""

    @staticmethod
    def get_user_stats(user):
        """Метод для получения отчетных данных для пользователя с правами 'owner'"""

        user_mailings = Mailing.objects.filter(owner=user)
        return {
            "attempts_all": MailingAttempt.objects.filter(mailing__in=user_mailings).count(),
            "attempts_success": MailingAttempt.objects.filter(
                mailing__in=user_mailings,
                status=MailingAttempt.SUCCESSFULLY
            ).count(),
            "recipients_all": Recipient.objects.filter(owner=user).count(),
            "messages_all": Message.objects.filter(owner=user).count(),
            "datetime_now": timezone.now(),
        }

    @staticmethod
    def get_manager_stats():
        """Метод для получения отчетных данных для пользователя с правами доступа 'is_manager'"""

        return {
            "attempts_all": MailingAttempt.objects.count(),
            "attempts_successfully": (MailingAttempt.objects.filter(status=MailingAttempt.SUCCESSFULLY)).count(),
            "recipients_all": Recipient.objects.all().count(),
            "messages_all": Message.objects.all().count(),
            "datetime_now": timezone.now(),
        }


class UserDataService:
    """Сервис для работы с данными пользователя"""

    def __init__(self, user):
        """Инициализация сервиса"""
        self.user = user

    @property
    def recipients(self) -> 'QuerySet[Recipient]':
        """Метод для получения клиентов текущего пользователя"""

        if hasattr(self.user, 'is_manager'):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.user)


    @property
    def mailings(self) -> 'QuerySet[Mailing]':
        """Метод для получения рассылок текущего пользователя"""

        if hasattr(self.user, 'is_manager'):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.user)


    @property
    def messages(self) -> 'QuerySet[Message]':
        """Получает QuerySet сообщений для авторизованного пользователя"""
        return Message.objects.filter(owner=self.user)

    @property
    def mailing_attempts(self) -> 'QuerySet[MailingAttempt]':
        """Получает QuerySet попыток рассылки для авторизованного пользователя"""
        return MailingAttempt.objects.filter(mailing__owner=self.user)
