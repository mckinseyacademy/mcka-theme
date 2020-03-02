from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import datetime, timedelta


class Command(BaseCommand):
    """
    THIS IS A CUSTOM COMMAND TO BE ADDED TO CRON JOB.
    IT DELETES ALL TEMP PROFILE AND COMPANY IMAGES OLDER THEN 12 HOURS.
    """
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        # do something here
        if default_storage.exists('images/' + settings.TEMP_IMAGE_FOLDER):
            dirs, files = default_storage.listdir('images/' + settings.TEMP_IMAGE_FOLDER)
            threshold = datetime.now() - timedelta(hours=12)
            for temp_file in files:
                try:
                    mod_time = default_storage.get_modified_time('images/' + settings.TEMP_IMAGE_FOLDER + temp_file)
                    if mod_time < threshold:
                        default_storage.delete('images/' + settings.TEMP_IMAGE_FOLDER + temp_file)
                except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
                    pass
