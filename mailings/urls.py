from django.urls import path
# from django.views.decorators.cache import cache_page

from mailings.apps import MailingsConfig
from mailings.views import RecipientListView, RecipientCreateView, RecipientDetailView, RecipientUpdateView, \
    RecipientDeleteView

app_name = MailingsConfig.name


urlpatterns = [
    path("mailings/", RecipientListView.as_view(), name="recipient_list"),
    path("mailings/create/", RecipientCreateView.as_view(), name="recipient_form"),
    path("mailings/<int:pk>/detail/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("mailings/<int:pk>/update/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("catalog/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_confirm_delete"),
]