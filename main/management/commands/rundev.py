from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import os
import subprocess
import signal
import atexit

assets_pid = None
class Command(BaseCommand):
    help = 'Runs the dev server and watches compileable assets'

    def handle(self, *args, **options):
        assets_pid = None

        port = '3000'
        if len(args) > 0:
            port = args[0]

        startup_message = "Starting dev server on port {0} with asset watcher...".format(port)
        self.stdout.write(startup_message)

        path = os.path.join(os.path.abspath('.'), 'manage.py')
        assets_proc = subprocess.Popen([path, 'assets', 'watch'])
        assets_pid = assets_proc.pid
        call_command('runserver', port)

    def kill_child():
        if assets_pid is None:
            pass
        else:
            os.kill(assets_pid, signal.SIGTERM)

    atexit.register(kill_child)
