"""
app configuration
"""
from django.apps import AppConfig


class APIDataManagerConfig(AppConfig):
    name = 'api_data_manager'
    verbose_name = 'data manager app'

    def ready(self):
        import api_data_manager.signals
