from django.apps import AppConfig


class AdminAprosConfig(AppConfig):
    name = 'admin'
    label = 'admin_apros'

    def ready(self):
        """
        Initialize admin app and import celery tasks
        """
        import admin.tasks  # pylint: disable=unused-variable
