from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpRequest, HttpResponse

from mailings.forms import RecipientForm, MessageForm
from mailings.models import Recipient, Message, Mailing


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


class MailingCreateView(CreateView):
    """Класс представления для добавления рассылок"""

    model = Mailing
    form_class = MailingForm    #пока нет формы
    success_url = reverse_lazy("mailings:mailing_list")

    def form_valid(self, form: RecipientForm) -> HttpResponse:
        """Обработка валидной формы - привязка рассылки к текущему пользователю"""

        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingDetailView(DetailView):
    """Класс для детального отображения данных рассылки"""

    model = Mailing


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
