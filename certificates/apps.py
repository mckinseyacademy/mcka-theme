"""
app configuration
"""
from django.apps import AppConfig


class CertificatesConfig(AppConfig):
    """
    Application Configuration for Certificates.
    """
    name = 'certificates'
    verbose_name = 'certificates app'

    def ready(self):
        """
        Initialize certificates app and import certificate tasks
        """
        import certificates.tasks # pylint: disable=unused-variable
