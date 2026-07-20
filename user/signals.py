from typing import Any

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import User


@receiver([post_save, post_delete], sender=User)
def clear_mailing_cache(sender: Any, **kwargs: Any) -> None:
    """Очищает кэш рассылок в Redis при изменениях"""

    keys_all = [
        "users_list_all",
        "users_active",
        "users_inactive",
    ]
    for key in keys_all:
        cache.delete(key)
        print(f"Удален ключ кэша: {key}")
