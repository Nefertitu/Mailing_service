from typing import Any

from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from core.mixins import StyleFormMixin

from .models import User


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
    """Форма для регистрации новых пользователей"""

    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        error_messages = {
            "email": {
               "required": "Email обязателен для регистрации",
                "unique": "Пользователь с таким Email уже существует",
            },
            "password1":{
                "required": "Это поле обязательно к заполнению",
            },
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализация формы"""
        super().__init__(*args, **kwargs)


class CustomUserChangeForm(StyleFormMixin, UserChangeForm):
    """Форма для редактирования профиля пользователя"""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone_number", "avatar")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализация формы"""
        super().__init__(*args, **kwargs)
        if "password" in self.fields:
            del self.fields["password"]


class CustomPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    """Кастомная форма для смены пароля с добавленными стилями"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализация формы"""
        super().__init__(**kwargs)


class UserManagerForm(StyleFormMixin, ModelForm):
    """Форма для блокировки пользователей менеджером"""

    class Meta:
        model = User
        fields = ("email", "is_active",)
