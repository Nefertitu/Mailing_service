import secrets
from typing import Optional, Type, Any

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from config.settings import EMAIL_HOST_USER

from .forms import CustomPasswordChangeForm, CustomUserChangeForm, CustomUserCreationForm, UserManagerForm
from .models import User


class RegisterView(CreateView):
    """Представление для регистрации новых пользователей"""

    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("user:login")

    def form_valid(self, form: CustomUserCreationForm) -> HttpResponse:
        """Обрабатывает валидную форму регистрации"""
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/user/email-confirm/{token}/"
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
    return redirect(reverse("user:login"))


class RegisterUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля пользователя"""

    model = User
    form_class = CustomUserChangeForm
    template_name = "user/user_update.html"
    success_url = reverse_lazy("user:user_list")

    def get_object(self, queryset: Optional[QuerySet] = None) -> User:
        """Возвращает текущего авторизованного пользователя"""

        object = super().get_object()
        user = self.request.user

        if user.is_manager and user.has_perm("user.can_block_users") and not object.is_superuser:
            return object
        raise PermissionDenied("Нет прав для редактирования этого профиля")

    def get_form_class(self) -> Type[forms.BaseForm]:
        """Возвращает класс формы в зависимости от прав пользователя"""

        user = self.request.user
        object = self.get_object()

        if user == object:
            return CustomUserChangeForm
        elif user != object and user.is_manager and user.has_perm("user.can_block_users"):
            return UserManagerForm

        raise PermissionDenied


class PasswordChangeView(DjangoPasswordChangeView):
    """Кастомное представление для смены пароля"""

    form_class = CustomPasswordChangeForm
    template_name = "user/password_change.html"
    success_url = reverse_lazy("user:user_update")


class UserListView(ListView):
    """Представление для списка пользователей"""

    model = User

    def get_queryset(self):
        """Возвращает список пользователей (только для менеджеров)"""
        if self.request.user.is_manager:
            return User.objects.all()


    def get_context_data(self, **kwargs):
        """Добавляет сообщение о пустом списке пользователей в контекст"""

        context = super().get_context_data(**kwargs)

        if not context["object_list"].exists():
            context["empty_users"] = "Пока не зарегистрировано ни одного пользователя"
        return context



