from typing import Any, Type

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from mailings.models import Mailing


@receiver(post_save, sender=Mailing)
def check_mailing_completion(sender: Type[Mailing], instance: Mailing, **kwargs: Any) -> None:
    """Автоматически завершает рассылку, если end_at наступил"""
    if instance.update_status():
        instance.save()

@receiver([post_save, post_delete], sender=Mailing)
def clear_mailing_cache(sender, **kwargs: Any):
    """Очищает кэш рассылок в Redis при изменениях"""

    keys_all = [
        'mailings_list_all',
        'mailings_active',
        'mailings_inactive',
    ]
    for key in keys_all:
        cache.delete(key)
        print(f"Удален ключ кэша: {key}")

    User = get_user_model()
    for user in User.objects.all():
        key = f"mailing_list_{user.pk}"
        cache.delete(key)
        print(f"Удален ключ кэша: {key}")



