import os
from typing import Any

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from mailings.models import Mailing, MailingAttempt


class Command(BaseCommand):
    """Команда для отправки рассылки через интерфейс пользователя и командную строку"""

    help = "Тестовая рассылка"

    def handle(self, *args: Any, **options: Any) -> None:
        """Основной метод выполнения команды. """

        time_now = timezone.now()

        active_mailings = Mailing.objects.filter(
            models.Q(
                start_at__lte=time_now,
                end_at__gte=time_now,
                status=Mailing.CREATED
            ) | models.Q(
                status=Mailing.LAUNCHED,
                end_at__gte=time_now
            )
        )

        if not active_mailings:
            self.stdout.write("No active mailings found")

        for mailing in active_mailings:
            self.stdout.write(f"Processing mailing ID: {mailing.pk}")
            recipients = mailing.recipients.all()
            message = mailing.message

            if mailing.status in [mailing.COMPLETED]:
                return

            if mailing.status == mailing.CREATED:
                mailing.status = mailing.LAUNCHED
                mailing.start_at = timezone.now()
                mailing.save()

            for recipient in recipients:
                try:
                    send_mail(
                        subject=message.title,
                        message=message.body,
                        from_email=os.getenv("EMAIL_HOST_USER"),
                        recipient_list=[recipient.email],
                        fail_silently=False
                    )
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status=MailingAttempt.SUCCESSFULLY,
                        server_response=f"Successfully send to {recipient.email}"
                    )
                    self.stdout.write(f"Successfully send to {recipient.email}")
                except Exception as e:
                    error_msg = str(e)
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status=MailingAttempt.UNSUCCESSFUL,
                        server_response=error_msg
                    )
                    self.stdout.write(f"Failed to send to {recipient.email}: {error_msg}")
        self.stdout.write("Finished processing all active mailings")
