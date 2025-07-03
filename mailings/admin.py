from django.contrib import admin

from mailings.forms import MailingForm, MessageForm, RecipientForm
from mailings.models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Администрирование клиентов. Позволяет управлять
    получателями, с возможностью фильтрации и поиска."""

    list_display = (
        "id",
        "email",
        "fullname",
        "owner",
    )
    list_filter = ("email",)
    search_fields = (
        "email",
        "fullname",
    )
    list_editable = ("owner",)
    form = RecipientForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Администрирование сообщений. Позволяет управлять
    сообщениями, с возможностью фильтрации и поиска."""

    list_display = ("id", "title", "body", "owner")
    list_filter = ("title",)
    search_fields = ("title",)
    form = MessageForm


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Администрирование рассылок. Позволяет управлять
    рассылками, с возможностью фильтрации и поиска."""

    list_display = ("id", "start_at", "end_at", "status")
    list_filter = ("start_at", "end_at", "status")
    search_fields = (
        "start_at",
        "end_at",
        "status",
    )
    form = MailingForm


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Администрирование попыток рассылок"""

    list_display = ("datetime_attempt", "status", "server_response")
    list_filter = ("datetime_attempt", "status")
    search_fields = (
        "datetime_attempt",
        "status",
    )
