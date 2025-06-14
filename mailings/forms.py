from django.forms import ModelForm

from core.mixins import StyleFormMixin
from mailings.models import Recipient


class RecipientForm(StyleFormMixin, ModelForm):
    """Форма для создания и редактирования получателей рассылок"""

    class Meta:
        model = Recipient
        exclude = [
            "owner",
        ]
