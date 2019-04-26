from django.core.management.base import BaseCommand

from admin.models import SelfRegistrationRoles


class Command(BaseCommand):
    help = 'Updates the Self registration roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--revert', '-r', action='store_true', dest='revert'
        )

    def handle(self, *args, **options):
        revert = options['revert']
        if revert:
            SelfRegistrationRoles.objects.filter(
                option_text='Other'
            ).update(
                option_text='Other (please describe below)'
            )
        else:
            SelfRegistrationRoles.objects.filter(
                option_text='Other (please describe below)'
            ).update(
                option_text='Other'
            )
