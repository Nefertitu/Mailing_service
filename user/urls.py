from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetCompleteView
from django.urls import path

from user.apps import UserConfig
from user.views import (
    PasswordChangeView,
    PasswordResetCustomConfirmView,
    PasswordResetCustomDoneView,
    PasswordResetCustomView,
    RegisterUpdateView,
    RegisterView,
    SuccessConfirmView,
    SuccessRegisterView,
    UserListView,
    email_verification,
)

app_name = UserConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="mailings:start"), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("success_register/", SuccessRegisterView.as_view(), name="success_register"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("success_confirm/", SuccessConfirmView.as_view(), name="success_confirm"),
    path("profile/update/<int:pk>/", RegisterUpdateView.as_view(), name="user_update"),
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("password_reset/", PasswordResetCustomView.as_view(), name="password_reset_custom"),
    path("password_reset/done/", PasswordResetCustomDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetCustomConfirmView.as_view(), name="password_reset_confirm"),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(template_name="user/success_confirm.html"),
        name="password_reset_complete",
    ),
]
