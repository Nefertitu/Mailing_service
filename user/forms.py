from typing import Any

from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm, UserCreationForm

from core.mixins import StyleFormMixin

from .models import User


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
    """Форма для регистрации новых пользователей"""

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

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
        super().__init__(*args, **kwargs)
