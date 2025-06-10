import secrets
from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView

from config.settings import EMAIL_HOST_USER

from .forms import CustomPasswordChangeForm, CustomUserChangeForm, CustomUserCreationForm
from .models import User


class RegisterView(CreateView):
    """Представление для регистрации новых пользователей"""

    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form: CustomUserCreationForm) -> HttpResponse:
        """Обрабатывает валидную форму регистрации"""
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Для подтверждения почты перейдите по ссылке - {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request: HttpRequest, token: str) -> HttpResponse:
    """Подтверждает email пользователя по токену"""
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class RegisterUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля пользователя"""

    model = User
    form_class = CustomUserChangeForm
    template_name = "users/user_update.html"
    success_url = reverse_lazy("catalog:product_list")

    def get_object(self, queryset: Optional[QuerySet] = None) -> User:
        """Возвращает текущего авторизованного пользователя"""
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Пользователь не аутентифицирован")
        return user


class PasswordChangeView(DjangoPasswordChangeView):
    """Кастомное представление для смены пароля"""

    form_class = CustomPasswordChangeForm
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:user_update")

