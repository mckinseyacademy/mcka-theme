from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import os, subprocess, signal, atexit


class Command(BaseCommand):
    help = 'Runs the dev server and watches compileable assets'

    def handle(self, *args, **options):
        global assets_pid
        
        port = 8000
        if len(args) > 0:
            port = args[0]

        startup_message = "Starting dev server on port {0} with asset watcher...".format(port)
        self.stdout.write(startup_message)
        
        path = os.path.join(os.path.abspath('.'), 'manage.py')
        assets_proc = subprocess.Popen([path, 'assets', 'watch'])
        assets_pid = assets_proc.pid
        run_server_cmd = "runserver {0}".format(port)
        call_command('runserver', port)

    def kill_child():
        if assets_pid is None:
            pass
        else:
            os.kill(assets_pid, signal.SIGTERM)

    atexit.register(kill_child)
