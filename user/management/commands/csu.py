from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Команда для создания суперпользователя
    с предопределенными учетными данными"""

    def handle(self, *args: Any, **options: Any) -> None:
        """Добавляет суперпользователю email и пароль"""
        User = get_user_model()
        user = User.objects.create(email="superuser@example.com")
        user.set_password("123qwer")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully created user with email {user.email}!"))
