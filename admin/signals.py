from django.db.models.signals import post_save
from django.dispatch import receiver

from admin.models import ClientCustomization
from api_data_manager.organization_data import OrgDataManager, ORGANIZATION_PROPERTIES


@receiver(post_save, sender=ClientCustomization)
def delete_branding_data(sender, instance, **kwargs):
    OrgDataManager(instance.client_id).delete_cached_data(ORGANIZATION_PROPERTIES.BRANDING)
