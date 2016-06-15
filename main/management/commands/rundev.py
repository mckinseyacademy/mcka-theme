from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
import subprocess
import signal
import atexit

class Command(BaseCommand):
    help = 'Runs the dev server and watches compileable assets'

    def handle(self, *args, **options):
        global assets_watcher_pid
        assets_watcher_pid = None

        port = '3000'
        if len(args) > 0:
            port = args[0]

        startup_message = "Starting dev server on port {0} with asset watcher...".format(port)
        self.stdout.write(startup_message)

        path = os.path.join(os.path.abspath('.'), 'manage.py')
        assets_watcher_proc = subprocess.Popen([path, 'assets', 'watch'])
        assets_watcher_pid = assets_watcher_proc.pid
        print "Assets watcher PID IS: %d" % assets_watcher_pid
        call_command('runserver', port)

    def kill_child():
        if assets_watcher_pid:
            print "Killing assets watcher PID: %d" % assets_watcher_pid
            os.kill(assets_watcher_pid, signal.SIGTERM)
        else:
            print "No watcher to kill."

    atexit.register(kill_child)
