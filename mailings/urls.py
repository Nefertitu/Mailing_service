from django.urls import path
from django.views.decorators.cache import cache_page

from mailings.apps import MailingsConfig
from mailings.views import (
    HomeView,
    MailingAttemptDeleteView,
    MailingAttemptDetailView,
    MailingAttemptListView,
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    RecipientCreateView,
    RecipientDeleteView,
    RecipientDetailView,
    RecipientListView,
    RecipientUpdateView,
    SearchView,
    StartView,
    run_mailing_command,
)

app_name = MailingsConfig.name


urlpatterns = [
    path("start/", StartView.as_view(), name="start"),
    path("search/", SearchView.as_view(), name="search_result"),
    path("mailings/home/", HomeView.as_view(), name="home"),
    path("mailings/recipient/", (RecipientListView.as_view()), name="recipient_list"),
    path("mailings/run-mailing/", run_mailing_command, name="run_mailing"),
    path("mailings/recipient/create/", RecipientCreateView.as_view(), name="recipient_form"),
    path("mailings/recipient/<int:pk>/detail/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("mailings/recipient/<int:pk>/update/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("mailings/recipient/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_confirm_delete"),
    path("mailings/message/", (MessageListView.as_view()), name="message_list"),
    path("mailings/message/create/", MessageCreateView.as_view(), name="message_form"),
    path("mailings/message/<int:pk>/detail/", MessageDetailView.as_view(), name="message_detail"),
    path("mailings/message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("mailings/message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_confirm_delete"),
    path("mailings/mailing/", (MailingListView.as_view()), name="mailing_list"),
    path("mailings/mailing/create/", MailingCreateView.as_view(), name="mailing_form"),
    path("mailings/mailing/<int:pk>/detail/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/mailing/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailings/mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_confirm_delete"),
    path("mailings/mailingattempt/", MailingAttemptListView.as_view(), name="mailingattempt_list"),
    path("mailings/mailingattempt/<int:pk>/detail/", MailingAttemptDetailView.as_view(), name="mailingattempt_detail"),
    path(
        "mailings/mailingattempt/<int:pk>/delete/",
        MailingAttemptDeleteView.as_view(),
        name="mailingattempt_confirm_delete",
    ),
]
