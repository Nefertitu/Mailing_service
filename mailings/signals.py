from django.db.models.signals import post_save
from django.dispatch import receiver

from mailings.models import Mailing


@receiver(post_save, sender=Mailing)
def check_mailing_completion(sender, instance, **kwargs):
    """Автоматически завершает рассылку, если end_at наступил"""
    instance.update_status()