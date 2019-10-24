from django.core.management.base import BaseCommand

from admin.tasks import purge_old_import_records_and_csv_files


class Command(BaseCommand):
    help = 'Triggers background task for purging old import records'

    def handle(self, *args, **options):
        try:
            task_id = purge_old_import_records_and_csv_files.delay()
        except Exception as e:
            self.stderr.write(self.style.ERROR('Task failed to trigger with exception: "%s"' % str(e)))
        else:
            self.stdout.write(self.style.SUCCESS('Successfully triggered purge old import records task: "%s"'
                                                 % task_id))
