from django.core.management.base import BaseCommand

from admin.models import SelfRegistrationRoles


class Command(BaseCommand):
    help = 'Updates the Self registration roles'

    def handle(self, *args, **options):
        SelfRegistrationRoles.objects.filter(option_text='Other (please describe below)').update(option_text='Other')
