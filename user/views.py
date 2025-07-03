import secrets
from typing import Optional, Type, cast, Any

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from config.settings import EMAIL_HOST_USER
from .services import UserDataService

from .forms import CustomPasswordChangeForm, CustomUserChangeForm, CustomUserCreationForm, UserManagerForm
from .models import User


class RegisterView(CreateView):
    """Представление для регистрации новых пользователей"""

    model = User
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("user:success_register")

    def form_valid(self, form: CustomUserCreationForm) -> HttpResponse:
        """Обрабатывает валидную форму регистрации"""
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()

        self.request.session["new_user_email"] = user.email
        self.request.session.modified = True

        host = self.request.get_host()
        url = f"http://{host}/user/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Для подтверждения почты перейдите по ссылке - {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Для отображения страницы о завершении регистрации"""
        return reverse("user:success_register")


class SuccessRegisterView(TemplateView):
    template_name = "user/success_register.html"

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавляет в контекст 'email' нового пользователя"""

        context = super().get_context_data(**kwargs)
        context["email"] = self.request.session.get("new_user_email")
        return context


def email_verification(request: HttpRequest, token: str) -> HttpResponse:
    """Подтверждает email пользователя по токену"""

    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()

    request.session["new_user_email"] = user.email
    request.session.modified = True

    return redirect(reverse("user:success_confirm"))


class SuccessConfirmView(TemplateView):
    template_name = "user/success_confirm.html"

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавляет в контекст 'email' нового пользователя"""

        context = super().get_context_data(**kwargs)
        context["email"] = self.request.session.get("new_user_email")
        return context


class RegisterUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля пользователя"""

    model = User
    form_class = CustomUserChangeForm
    template_name = "user/user_update.html"

    def get_object(self, queryset: Optional[QuerySet] = None) -> User:
        """Возвращает текущего авторизованного пользователя"""

        if not self.request.user.is_authenticated:
            raise PermissionDenied("Пользователь не аутентифицирован")

        if queryset is None:
            queryset = self.get_queryset()

        object = queryset.get(pk=self.request.user.pk)

        if self.request.user.is_manager or self.request.user.has_perm("user.can_edit_users"):
            object = super().get_object(queryset)

        return object

    def get_form_class(self) -> Type[forms.BaseForm]:
        """Возвращает класс формы в зависимости от прав пользователя"""

        object = self.get_object()

        if not self.request.user.is_authenticated:
            raise PermissionDenied("Пользователь не аутентифицирован")

        user = self.request.user

        if user == object:
            return CustomUserChangeForm
        elif user != object and user.is_manager and user.has_perm("user.can_block_users"):
            return UserManagerForm

        raise PermissionDenied

    def get_success_url(self) -> str:
        """Возвращает URL для перенаправления после успешного действия"""

        user = cast(User, self.request.user)

        if user.is_manager or user.has_perm("user.can_edit_users"):
            return reverse("user:user_list")
        return reverse("mailings:home")


class PasswordChangeView(DjangoPasswordChangeView):
    """Кастомное представление для смены пароля"""

    form_class = CustomPasswordChangeForm
    template_name = "user/password_change.html"
    success_url = reverse_lazy("user:user_update")


class UserListView(ListView):
    """Представление для списка пользователей"""

    model = User

    def get_queryset(self) -> QuerySet[User]:
        """Возвращает список пользователей (только для менеджеров)"""

        if not self.request.user.is_authenticated:
            raise PermissionDenied("Доступ запрещен")

        users_service = UserDataService()
        user = self.request.user

        if user.is_manager:
            return users_service.get_users_from_cache(user=user)
        return User.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавляет сообщение о пустом списке пользователей в контекст"""

        context = super().get_context_data(**kwargs)

        if not context["object_list"]:
            context["empty_users"] = "Пока не зарегистрировано ни одного пользователя"
        return context


class PasswordResetCustomView(PasswordResetView):
    """Запрос на смену пароля"""

    template_name = "user/password_reset_custom.html"
    email_template_name = "user/password_reset_email_custom.html"
    success_url = reverse_lazy("user:password_reset_done")


class PasswordResetCustomConfirmView(PasswordResetConfirmView):
    """Кастомное представление для ввода нового пароля"""

    template_name = "user/password_reset_confirm.html"
    success_url = reverse_lazy("user:password_reset_complete")


class PasswordResetCustomDoneView(PasswordResetDoneView):
    """Кастомное представление страницы подтверждения отправки письма для сброса пароля"""

    template_name = "user/password_reset_done.html"


class PasswordResetCustomCompleteView(PasswordResetCompleteView):
    """Кастомное представление завершения сброса пароля"""

    template_name = "user/password_reset_complete.html"
    success_url = reverse_lazy("user:success_confirm")
    extra_email_context = {
        "site_name": "Mailing Service",
    }

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавляет данные в контекст - имя вебприложения"""

        context = super().get_context_data(**kwargs)

        context["site_name"] = "Mailing Service"
        return context
