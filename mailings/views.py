from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpRequest, HttpResponse

from mailings.forms import RecipientForm
from mailings.models import Recipient


class RecipientListView(ListView):
    """Класс для представления списка клиентов"""

    model = Recipient


class RecipientCreateView(CreateView):
    """Класс представления для добавления нового клиента"""

    model = Recipient
    form_class = RecipientForm    #пока нет формы
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

