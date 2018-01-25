"""
app configuration
"""
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class CertificatesConfig(AppConfig):
    """
    Application Configuration for Certificates.
    """
    name = 'certificates'
    verbose_name = _('certificates app')

    def ready(self):
        """
        Initialize certificates app and import certificate tasks
        """
        import certificates.tasks # pylint: disable=unused-variable
