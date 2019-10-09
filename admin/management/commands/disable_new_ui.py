from django.core.management.base import BaseCommand

from admin.models import ClientCustomization


class Command(BaseCommand):
    help = "Disable New UI for all companies except for companies with ids 775,807,101,17"

    def handle(self, *args, **options):
        company_ids_to_exclude = [775, 807, 101, 17]
        try:
            client_customizations = ClientCustomization.objects.exclude(client_id__in=company_ids_to_exclude)
            for client_customization in client_customizations:
                client_customization.new_ui_enabled = False
                client_customization.save()
                self.stdout.write("New UI disabled for Company: {}".format(client_customization.client_id))
        except Exception as e:
            self.stderr.write("This command failed because of '{}'.".format(e))
