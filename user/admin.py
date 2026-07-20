from django.contrib import admin

from user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Администрирование пользователей. Позволяет управлять
    пользователями, с возможностью фильтрации и поиска."""

    list_display = ("id", "email", "phone_number", "is_manager")
    list_filter = ("email",)
    search_fields = (
        "email",
        "phone_number",
    )
    list_editable = ("is_manager",)
