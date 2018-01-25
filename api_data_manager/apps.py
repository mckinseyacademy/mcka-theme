"""
app configuration
"""
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class APIDataManagerConfig(AppConfig):
    name = 'api_data_manager'
    verbose_name = _('data manager app')

    def ready(self):
        import api_data_manager.signals
