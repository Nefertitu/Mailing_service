import logging

from typing import Any, Type

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import QuerySet, Q
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponse, HttpRequest

from mailings.forms import RecipientForm, MessageForm, MailingForm, MailingManagerForm
from mailings.models import Recipient, Message, Mailing, MailingAttempt
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.management import call_command
from django.contrib import messages

from mailings.services import StatisticsService, UserDataService

logger = logging.getLogger("mailings")


class RecipientListView(LoginRequiredMixin, ListView):
    """Класс для представления списка клиентов"""

    model = Recipient

    def get_queryset(self):
        """Возвращает список клиентов пользователям с правами доступа"""

        queryset = super().get_queryset()
        if self.request.user.is_manager:
            return queryset
        else:
            return Recipient.objects.filter(owner=self.request.user)


    def get_context_data(self, **kwargs):
        """Добавляет сообщение о пустом списке получателей в контекст"""

        context = super().get_context_data(**kwargs)

        if not context["object_list"].exists():
            context["empty_recipients"] = "У вас пока не добавлено ни одного получателя"
        return context


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Класс представления для добавления нового клиента"""

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailings:recipient_list")

    def dispatch(self, request, *args, **kwargs):
        """Запрет доступа менеджерам на уровне входа в view"""
        if request.user.is_manager:
            raise PermissionDenied("Менеджерам запрещено создавать получателей")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: RecipientForm) -> HttpResponse:
        """Обработка валидной формы - привязка клиента к текущему пользователю"""

        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_recipients = Recipient.objects.filter(owner=self.request.user)
        context["existing_recipients"] = ", ".join(
            recipient.get_recipients_display(user=self.request.user)
            for recipient in user_recipients
        )
        return context


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """Класс для детального отображения карточки клиента"""

    model = Recipient

    def get_queryset(self):
        """Возвращает карточку клиента пользователю с правами менеджера"""

        queryset = super().get_queryset()
        if not self.request.user.is_manager:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Класс для редактирования существующего клиента"""

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailings:recipient_list")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Проверка прав доступа пользователя"""

        self.object = self.get_object()

        if request.user != self.object.owner:
            raise PermissionDenied("Вы не можете редактировать этого получателя")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        """Для отображения детальной страницы клиента после её редактирования"""
        return reverse("mailings:recipient_detail", args=[self.kwargs.get("pk")])


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Класс для удаления получателей"""

    model = Recipient
    success_url = reverse_lazy("mailings:recipient_list")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Проверка прав доступа пользователя"""

        self.object = self.get_object()

        if request.user != self.object.owner:
            raise PermissionDenied("Вы не можете удалять получателей")
        return super().dispatch(request, *args, **kwargs)


class MessageListView(LoginRequiredMixin, ListView):
    """Класс для представления списка сообщений"""

    model = Message
    paginate_by = 3

    def get_queryset(self):
        """Возвращает список сообщений пользователям с правами доступа"""

        queryset = super().get_queryset()
        if not self.request.user.is_manager:
            return queryset.filter(owner=self.request.user)
        raise PermissionDenied("Менеджеры не могут просматривать сообщения")

    def get_context_data(self,**kwargs):
        """Добавляет сообщение о пустом списке сообщений в контекст"""

        context = super().get_context_data(**kwargs)

        if not context["object_list"].exists():
            context["empty_messages"] = "У вас пока не создано ни одного сообщения"
        return context


class MessageCreateView(CreateView):
    """Класс представления для добавления сообщения"""

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")

    def dispatch(self, request, *args, **kwargs):
        """Запрет доступа менеджерам"""
        if request.user.is_manager:
            raise PermissionDenied("Менеджерам запрещено создавать сообщения")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: RecipientForm) -> HttpResponse:
        """Обработка валидной формы - привязка сообщения к текущему пользователю"""

        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDetailView(DetailView):
    """Класс для детального отображения карточки сообщения"""

    model = Message

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Проверка прав доступа пользователя"""

        self.object = self.get_object()

        if request.user != self.object.owner:
            raise PermissionDenied("Вы не можете просматривать сообщения")
        return super().dispatch(request, *args, **kwargs)


class MessageUpdateView(UpdateView):
    """Класс для редактирования существующего сообщения"""

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")

    def get_success_url(self) -> str:
        """Для отображения детальной страницы сообщения после её редактирования"""
        return reverse("mailings:message_detail", args=[self.kwargs.get("pk")])

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Проверка прав доступа пользователя"""

        self.object = self.get_object()

        if request.user != self.object.owner:
            raise PermissionDenied("Вы не можете редактировать сообщения")
        return super().dispatch(request, *args, **kwargs)


class MessageDeleteView(DeleteView):
    """Класс для удаления сообщения"""

    model = Message
    success_url = reverse_lazy("mailings:message_list")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Проверка прав доступа пользователя"""

        self.object = self.get_object()

        if request.user != self.object.owner:
            raise PermissionDenied("Вы не можете удалять сообщения")
        return super().dispatch(request, *args, **kwargs)


class MailingListView(LoginRequiredMixin, ListView):
    """Класс для представления списка рассылок"""

    model = Mailing

    def get_base_queryset(self):
        """Базовый 'queryset' с обновленными статусами рассылок"""

        queryset = super().get_queryset()
        for mailing in queryset:
            mailing.update_status()
        return queryset

    def get_queryset(self):
        """Фильтрация по правам доступа"""

        queryset = self.get_base_queryset()
        if not self.request.user.is_manager:
            queryset = queryset.filter(owner=self.request.user, is_active=True)
        return queryset

    def get_context_data(self,**kwargs):
        """Добавляет сообщение о пустом списке рассылок в контекст"""

        context = super().get_context_data(**kwargs)

        if not context["object_list"].exists():
            context["empty_mailings"] = "У вас пока нет ни одной рассылки"
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Класс представления для добавления рассылок"""

    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailings:mailing_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_manager:
            form.fields["recipients"].queryset = Recipient.objects.filter(owner=self.request.user)
            form.fields["message"].queryset = Message.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form:MailingForm) -> HttpResponse:
        """Обработка валидной формы - привязка рассылки к текущему пользователю"""

        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingDetailView(LoginRequiredMixin, DetailView):
    """Класс для детального отображения данных рассылки
    и обработка отправки"""

    model = Mailing


    def post(self, request, *args: Any, **kwargs: Any):
        """Обработка отправки рассылки"""

        mailing = self.get_object()
        time_now = timezone.now()

        is_active = Mailing.objects.filter(
            models.Q(
                start_at__lte=time_now,
                end_at__gte=time_now,
                status=Mailing.CREATED
            ) | models.Q(
                status=Mailing.LAUNCHED,
                end_at__gte=time_now
            ),
        pk=mailing.pk
        ).exists()

        if not is_active:
            messages.error(request, "Эта рассылка не активна (неверный статус или даты)")
            logger.warning(request, "Эта рассылка не активна (неверный статус или даты)")
            return redirect('mailings:mailing_detail', pk=mailing.pk)

        mailing.send()
        mailing.update_status()
        messages.success(request, f"Рассылка '{mailing.message.title}' отправлена!")
        logger.info(f"Рассылка '{mailing.message.title}' успешно отправлена!")

        return redirect('mailings:mailing_detail', pk=mailing.pk)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Класс для редактирования существующей рассылки"""

    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailings:mailing_list")

    def get_success_url(self) -> str:
        """Для отображения детальной страницы рассылки после её редактирования"""
        return reverse("mailings:mailing_detail", args=[self.kwargs.get("pk")])

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Проверка прав доступа пользователя"""

        self.object = self.get_object()

        if request.user != self.object.owner:
            raise PermissionDenied("Вы не можете редактировать рассылки")
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self) -> Type[forms.BaseForm]:
        """Возвращает класс формы в зависимости от прав пользователя"""

        user = self.request.user
        if user == self.object.owner:
            return MailingForm
        if user.has_perm("mailings.can_disable_mailings"):
            return MailingManagerForm
        raise PermissionDenied


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Класс для удаления рассылки"""

    model = Mailing
    success_url = reverse_lazy("mailings:mailing_list")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Проверка прав доступа пользователя"""

        self.object = self.get_object()

        if request.user != self.object.owner:
            raise PermissionDenied("Вы не можете удалять рассылки")
        return super().dispatch(request, *args, **kwargs)


class MailingAttemptListView(LoginRequiredMixin, ListView):
    """Класс для представления списка попыток рассылок"""

    model = MailingAttempt
    paginate_by = 10
    ordering = ["-datetime_attempt", "pk"]


    def get_queryset(self) -> QuerySet:
        """Фильтрация попыток рассылки в зависимости от прав пользователя"""

        queryset = super().get_queryset()

        if not self.request.user.is_manager:
            user_mailings = Mailing.objects.filter(owner=self.request.user)
            queryset = queryset.filter(mailing__in=user_mailings)
            return queryset.order_by("-datetime_attempt", "pk")
        raise PermissionDenied("Менеджеры не могут просматривать список попыток рассылок")

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст общее количество попыток в зависимости
        от прав доступа. Добавляет в контекст соответствующее сообщение
        при отсутствии попыток рассылок"""

        context = super().get_context_data(**kwargs)

        if not context["object_list"].exists():
            context["empty_mailingattempts"] = "У вас пока нет попыток рассылок"

        if self.request.user.is_manager:
            context["total_count"] = MailingAttempt.objects.count()
        else:
            user_mailings = Mailing.objects.filter(owner=self.request.user)
            context["total_count"] = MailingAttempt.objects.filter(mailing__in=user_mailings).count()

        return context


class MailingAttemptDetailView(LoginRequiredMixin, DetailView):
    """Класс для детального отображения попытки рассылки"""

    model = MailingAttempt

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Проверка прав доступа пользователя"""

        self.object = self.get_object()

        if self.request.user.is_manager:
            raise PermissionDenied("Менеджеры не могут смотреть детальную информацию о попытках рассылок")
        return super().dispatch(request, *args, **kwargs)


class MailingAttemptDeleteView(LoginRequiredMixin, DeleteView):
    """Класс для удаления рассылки"""

    model = MailingAttempt
    success_url = reverse_lazy("mailings:mailingattempt_list")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        """Проверка прав доступа пользователя"""

        self.object = self.get_object()

        if self.request.user.is_manager:
            raise PermissionDenied("Менеджеры не могут удалять рассылки")
        return super().dispatch(request, *args, **kwargs)


@require_POST
def run_mailing_command(request):
    """Вызов команды и отправка рассылок"""

    if request.method == "POST":
        try:
            call_command("send_mailings")
            messages.success(request, "Рассылка успешно отправлена!")
        except Exception as e:
            messages.error(request, f"Ошибка: {str(e)}")
    return redirect(request.POST.get("next", "/"))


class HomeView(View):
    """Класс для отображения главной страницы"""
    template_name = "home.html"

    def get(self, request, *args: Any, **kwargs: Any):
        """Получение контекста для отображения на главной странице"""

        stats_service = StatisticsService()
        context = stats_service.get_manager_stats() if request.user.is_manager else stats_service.get_user_stats(
            request.user)
        return render(request, "mailings/home.html", context)

class StartView(TemplateView):
    """Класс для отображения стартовой страницы"""

    template_name = "mailings/start.html"
    success_url = reverse_lazy("mailings:start")
    context_object_name = "results"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["greetings"] = "Приветствуем Вас в сервисе рассылок Mailing Service!"
        return context


class SearchView(ListView):
    """Класс для поиска контекста в приложении 'Mailing Service'"""

    template_name = "mailings/search_result.html"
    paginate_by = 10
    context_object_name = "results"

    def get_queryset(self):
        """Поиск контекста"""

        query = self.request.GET.get('q', '').strip()
        if not query:
            return []
        user = self.request.user
        results = []

        # 1. Поиск получателей
        recipients = Recipient.objects.filter(
            Q(email__icontains=query) |
            Q(fullname__icontains=query)
        )
        if user.is_manager:
            recipients = recipients.all()
            results += list(recipients)
        elif not user.is_manager:
            recipients = recipients.filter(owner=user)
            results += list(recipients.select_related('owner'))



        # 2. Поиск сообщений
        messages = Message.objects.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query)
        )
        if not user.is_manager:
            messages = messages.filter(owner=user)
            results += list(messages.select_related('owner'))
        results += ""

        # 3. Поиск рассылок
        mailings = Mailing.objects.filter(
            Q(status__icontains=query) |
            Q(message__title__icontains=query) |
            Q(owner__email__icontains=query)
        )
        if user.is_manager:
            mailings = mailings.all()
            results += list(mailings)
        elif not user.is_manager:
            mailings = mailings.filter(owner=user)
            results += list(mailings.select_related('message', 'owner'))

        # 4. Поиск попыток рассылок
        attempts = MailingAttempt.objects.filter(
            Q(status__icontains=query) |
            Q(server_response__icontains=query) |
            Q(mailing__message__title__icontains=query)
        )
        if not user.is_manager:
            attempts = attempts.filter(mailing__owner=user)
            results += list(attempts.select_related('mailing', 'mailing__message'))
        results += ""

        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
