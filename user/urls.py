from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from core.mixins import StyleFormMixin
from user.apps import UserConfig
from user.views import PasswordChangeView, RegisterUpdateView, RegisterView, email_verification, UserListView


app_name = UserConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    # path("password-reset/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="mailings:start"), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("profile/update/<int:pk>/", RegisterUpdateView.as_view(), name="user_update"),
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
]
