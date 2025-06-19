from typing import Any

from django import forms
from django.forms import BooleanField, ChoiceField, ModelMultipleChoiceField


class StyleFormMixin(forms.Form):
    """Миксин для стилизации полей формы"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализация миксина с настройкой атрибутов виджетов"""
        super().__init__(*args, **kwargs)

        for fild_name, fild in self.fields.items():
            if isinstance(fild, (forms.BooleanField, forms.ModelMultipleChoiceField)):
                fild.widget.attrs["class"] = "form-check-input",
                fild.widget.attrs["wrapper-class"] = "form-check form-check-inline",
            elif isinstance(fild, ChoiceField):
                fild.widget.attrs["class"] = "form-select"
            else:
                fild.widget.attrs["class"] = "form-control"


