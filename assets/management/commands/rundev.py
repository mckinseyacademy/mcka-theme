from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import os, subprocess, signal, atexit


class Command(BaseCommand):
    help = 'Runs the dev server and watches compileable assets'

    def handle(self, *args, **options):
        global assets_pid
        
        self.stdout.write('Starting dev server with asset watcher...')
        
        path = os.path.join(os.path.abspath('.'), 'manage.py')
        assets_proc = subprocess.Popen([path, 'assets', 'watch'])
        assets_pid = assets_proc.pid
        call_command('runserver')

    def kill_child():
        if assets_pid is None:
            pass
        else:
            os.kill(assets_pid, signal.SIGTERM)

    atexit.register(kill_child)
        