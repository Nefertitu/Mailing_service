from typing import Any

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Команда для наполнения базы данных группой 'Менеджеры'"""

    help = "Создает группу 'Менеджеры' и назначает ей разрешения"

    def handle(self, *args: Any, **options: Any) -> None:
        """Основной метод выполнения команды. Создает группу `Менеджеры`ю
        Назначает разрешения."""

        manager_group, created = Group.objects.get_or_create(name="manager")

        permissions = Permission.objects.filter(
            codename__in=[
                "can_disable_mailings",
                "can_view_mailings",
                "can_view_recipients",
                "can_block_users",
            ]
        )

        manager_group.permissions.set(permissions)

        if created:
            self.stdout.write(self.style.SUCCESS("Группа 'Менеджеры' успешно создана!"))
        else:
            self.stdout.write(self.style.WARNING("Группа 'Менеджеры' уже существует."))
