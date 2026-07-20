from typing import Any, Type

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from mailings.models import Mailing, Message, Recipient


@receiver(post_save, sender=Mailing)
def check_mailing_completion(sender: Type[Mailing], instance: Mailing, **kwargs: Any) -> None:
    """Автоматически завершает рассылку, если end_at наступил"""
    if instance.update_status():
        instance.save()


@receiver([post_save, post_delete], sender=[Mailing, Recipient, Message])
def clear_mailing_cache(sender: Any, **kwargs: Any) -> None:
    """Очищает кэш рассылок в Redis при изменениях"""

    keys_all = [
        "mailings_list_all",
        "recipients_list_all",
        "mailings_active",
        "mailings_inactive",
    ]
    for key in keys_all:
        cache.delete(key)
        print(f"Удален ключ кэша: {key}")

    User = get_user_model()
    for user in User.objects.all():
        user_keys = [
            f"mailings_list_{user.pk}",
            f"messages_list_{user.pk}",
            f"recipients_list_{user.pk}",
        ]
        for key in user_keys:
            cache.delete(key)
            print(f"Удален ключ кэша пользователя {user.email}: {key}")
