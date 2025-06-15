from django.urls import path
# from django.views.decorators.cache import cache_page

from mailings.apps import MailingsConfig
from mailings.views import RecipientListView, RecipientCreateView, RecipientDetailView, RecipientUpdateView, \
    RecipientDeleteView, MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView, MessageDetailView

app_name = MailingsConfig.name


urlpatterns = [
    path("mailings/", RecipientListView.as_view(), name="recipient_list"),
    path("mailings/create/", RecipientCreateView.as_view(), name="recipient_form"),
    path("mailings/<int:pk>/detail/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("mailings/<int:pk>/update/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("mailings/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_confirm_delete"),
    path("mailings/message/", MessageListView.as_view(), name="message_list"),
    path("mailings/message/create/", MessageCreateView.as_view(), name="message_form"),
    path("mailings/message/<int:pk>/detail/", MessageDetailView.as_view(), name="message_detail"),
    path("mailings/message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("mailings/message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_confirm_delete"),

]