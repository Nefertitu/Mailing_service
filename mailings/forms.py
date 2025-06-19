from django import forms
from django.forms import ModelForm
from django.template.context_processors import request

from core.mixins import StyleFormMixin
from mailings.models import Recipient, Message, Mailing


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
        queryset=Recipient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Выберите получателей"
    )

    class Meta:
        model = Mailing
        exclude = [
            "owner",
        ]

    def clean(self):
        cleaned_data = super().clean()


        if cleaned_data.get("select_all"):
            cleaned_data["recipients"] = self.fields["recipients"]

        return cleaned_data
