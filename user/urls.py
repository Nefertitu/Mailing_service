from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from user.apps import UserConfig
from user.views import PasswordChangeView, RegisterUpdateView, RegisterView, email_verification

app_name = UserConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="catalog:product_list"), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("profile/update/", RegisterUpdateView.as_view(), name="user_update"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
]
