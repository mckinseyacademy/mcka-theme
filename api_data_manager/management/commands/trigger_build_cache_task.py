from django.core.management.base import BaseCommand

from api_data_manager.tasks import build_common_data_cache


class Command(BaseCommand):
    help = 'Triggers background tasks for building cache'

    def handle(self, *args, **options):
        try:
            task_id = build_common_data_cache.delay()
        except Exception as e:
            self.stderr.write(self.style.ERROR('Tasks failed to trigger with exception: "%s"' % e.message))
        else:
            self.stdout.write(self.style.SUCCESS('Successfully triggered cache building background task: "%s"'
                                                 % task_id))
