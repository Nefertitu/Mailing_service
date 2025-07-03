from typing import Optional, Any

from django.core.cache import cache
from django.db.models import QuerySet

from config.settings import CACHE_ENABLED
from user.models import User


class UserDataService:
    """Сервис для работы с данными пользователей"""

    def get_users_from_cache(self, user: "Optional[User]") -> QuerySet[User, User] | None | Any:
        """Получает данные о клиентах из кэша, если кэш пуст,
        получает данные из базы данных"""

        if not CACHE_ENABLED:
            print("Кэш отключен")
            if user.is_manager:
                return User.objects.all()

        if user.is_manager:
            key = "users_list_all"

            users = cache.get(key)
            print(f"Попытка получить по ключу: {key}")

            if users is not None:
                print(f"Данные найдены в кэше: {key}")
                return users
            print("Данные не найдены в кэше, запрос к БД")

            if user.is_manager:
                users = User.objects.all()

            cache.set(key, users)
            print(f'Данные сохранены в кэше по ключу: {key}')
            return users
