from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import os, subprocess


class Command(BaseCommand):
    help = 'Runs the dev server and watches compileable assets'

    def handle(self, *args, **options):
        self.stdout.write('Starting dev server with asset watcher...')
        
        path = os.path.join(os.path.abspath('.'), 'manage.py')
        subprocess.Popen([path, 'assets', 'watch'])
        call_command('runserver')
        