from django import forms
from django.forms import ModelForm
from django.template.context_processors import request

from core.mixins import StyleFormMixin
from mailings.models import Recipient, Message, Mailing
from mailings.services import UserDataService
from user.models import User


class RecipientForm(StyleFormMixin, ModelForm):
    """Форма для создания и редактирования получателей рассылок"""

    class Meta:
        model = Recipient
        exclude = [
            "owner",
        ]


class MessageForm(StyleFormMixin, ModelForm):
    """Форма для создания и редактирования сообщений"""

    class Meta:
        model = Message
        exclude = [
            "owner",
        ]

class MailingForm(StyleFormMixin, ModelForm):
    """Форма для создания и редактирования рассылок"""

    recipients = forms.ModelMultipleChoiceField(
        queryset=Recipient.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Выберите получателей"
    )
    message = forms.ModelChoiceField(
        queryset=Message.objects.none(),
        widget=forms.Select,
        required=False,
        label="Выберите темы сообщений",
    )

    class Meta:
        model = Mailing
        exclude = [
            "owner",
            "is_active",
        ]
        widgets = {
            'start_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'next_run': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }


class MailingManagerForm(StyleFormMixin, ModelForm):
    """Форма для отключения рассылок менеджером"""

    class Meta:
        model = Mailing
        fields = ("is_active",)

