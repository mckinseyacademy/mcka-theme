from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'
    label = 'main'

    def ready(self):
        import main.signals  # noqa: F401
