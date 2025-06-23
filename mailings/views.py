import logging
from typing import Any

from django.db import models
from django.db.models import QuerySet
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponse

from mailings.forms import RecipientForm, MessageForm, MailingForm
from mailings.models import Recipient, Message, Mailing, MailingAttempt
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.core.management import call_command
from django.contrib import messages


logger = logging.getLogger("mailings")


class RecipientListView(ListView):
    """Класс для представления списка клиентов"""

    model = Recipient


class RecipientCreateView(CreateView):
    """Класс представления для добавления нового клиента"""

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailings:recipient_list")

    def form_valid(self, form: RecipientForm) -> HttpResponse:
        """Обработка валидной формы - привязка клиента к текущему пользователю"""

        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientDetailView(DetailView):
    """Класс для детального отображения карточки клиента"""

    model = Recipient


class RecipientUpdateView(UpdateView):
    """Класс для редактирования существующего клиента"""

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailings:recipient_list")

    def get_success_url(self) -> str:
        """Для отображения детальной страницы клиента после её редактирования"""
        return reverse("mailings:recipient_detail", args=[self.kwargs.get("pk")])


class RecipientDeleteView(DeleteView):
    """Класс для удаления товара"""

    model = Recipient
    success_url = reverse_lazy("mailings:recipient_list")


class MessageListView(ListView):
    """Класс для представления списка сообщений"""

    model = Message
    paginate_by = 3


class MessageCreateView(CreateView):
    """Класс представления для добавления сообщения"""

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form: RecipientForm) -> HttpResponse:
        """Обработка валидной формы - привязка сообщения к текущему пользователю"""

        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDetailView(DetailView):
    """Класс для детального отображения карточки сообщения"""

    model = Message


class MessageUpdateView(UpdateView):
    """Класс для редактирования существующего сообщения"""

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")

    def get_success_url(self) -> str:
        """Для отображения детальной страницы сообщения после её редактирования"""
        return reverse("mailings:message_detail", args=[self.kwargs.get("pk")])


class MessageDeleteView(DeleteView):
    """Класс для удаления сообщения"""

    model = Message
    success_url = reverse_lazy("mailings:message_list")


class MailingListView(ListView):
    """Класс для представления списка рассылок"""

    model = Mailing

    def get_queryset(self):
        """Обновление статуса рассылок"""

        queryset = super().get_queryset()
        for mailing in queryset:
            mailing.update_status()
        return queryset


class MailingCreateView(CreateView):
    """Класс представления для добавления рассылок"""

    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailings:mailing_list")

    def form_valid(self, form:MailingForm) -> HttpResponse:
        """Обработка валидной формы - привязка рассылки к текущему пользователю"""

        form.instance.owner = self.request.user
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        """Добавляет данные в контекст"""

        context = super().get_context_data(**kwargs)
        context["select_all"] = True
        all_recipients = Recipient.objects.all()
        context["all_emails"] = ", ".join([recipient.email for recipient in all_recipients])
        if context["select_all"] == "on":
            context["recipients"] =  context["all_emails"]

        return context


class MailingDetailView(DetailView):
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


class MailingUpdateView(UpdateView):
    """Класс для редактирования существующей рассылки"""

    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailings:mailing_list")

    def get_success_url(self) -> str:
        """Для отображения детальной страницы рассылки после её редактирования"""
        return reverse("mailings:mailing_detail", args=[self.kwargs.get("pk")])


class MailingDeleteView(DeleteView):
    """Класс для удаления рассылки"""

    model = Mailing
    success_url = reverse_lazy("mailings:mailing_list")


class MailingAttemptListView(ListView):
    """Класс для представления списка попыток рассылок"""

    model = MailingAttempt
    paginate_by = 10
    ordering = ["-datetime_attempt", "pk"]

    def get_queryset(self) -> QuerySet:
        """Возвращает ограниченный queryset, содержащий только первые 20 записей"""
        return super().get_queryset()[:20]

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавляет в контекст шаблона общее количество попыток рассылки"""

        context = super().get_context_data(**kwargs)
        context["total_count"] = MailingAttempt.objects.all().count()
        return context


class MailingAttemptDetailView(DetailView):
    """Класс для детального отображения попытки рассылки"""

    model = MailingAttempt


class MailingAttemptDeleteView(DeleteView):
    """Класс для удаления рассылки"""

    model = MailingAttempt
    success_url = reverse_lazy("mailings:mailingattempt_list")


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

    def get(self, request, *args: Any, **kwargs: Any):
        """Получение контекста для отображения на главной странице"""

        context = {
            "attempts_all": MailingAttempt.objects.all().count(),
            "attempts_successfully": (MailingAttempt.objects.filter(status=MailingAttempt.SUCCESSFULLY)).count(),
            "recipients_all": Recipient.objects.all().count(),
            "messages_all": Message.objects.all().count(),
            "datetime_now": timezone.now(),
        }
        return render(request, "mailings/home.html", context)
