from django.apps import AppConfig


class MailingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mailings"

    def ready(self):
        """Импорт сигналов"""
        from mailings import signals
        print(f"Сигналы загружены: {signals.__name__}")
