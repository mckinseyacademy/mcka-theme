from django.core.management.base import BaseCommand
from django.utils import timezone

from admin.models import ClientCustomization


class Command(BaseCommand):
    help = (
        "Enable New UI for all the companies "
        "by default it will update for only "
        "those companies which are using old UI."
        "Use --all / -a for all companies."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--all', '-a', action='store_true', dest='all',
            help='Update new UI and new UI date for all companies '
                 'including those which were already using new UI.',
        )

    def handle(self, *args, **options):
        process_all = options['all']
        try:
            if process_all:
                companies = ClientCustomization.objects.all()
                message = "No Company Found"
            else:
                companies = ClientCustomization.objects.filter(new_ui_enabled=False)
                message = "No Old UI Company Found"
            if companies.exists():
                for company in companies:
                    company.new_ui_enabled = True
                    company.new_ui_enabled_at = timezone.now()
                    company.save()

                    self.stdout.write("New UI enabled for Company: {}".format(company.client_id))
            else:
                self.stdout.write(message)
        except Exception as e:
            self.stderr.write("This command failed because of '{}'.".format(e.message))
