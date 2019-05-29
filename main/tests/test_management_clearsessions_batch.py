from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.sessions.models import Session
from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
@freeze_time('2019-05-05')
class ClearSessionsBarchCommandTestCase(TestCase):

    def setUp(self):
        self.start_date = date = timezone.now() - timezone.timedelta(days=60)
        self.end_date = timezone.now() + timezone.timedelta(days=30)
        while date < self.end_date:
            Session.objects.create(
                session_key=date.isoformat(),
                expire_date=date,
            )
            date += timezone.timedelta(days=1)

    def test_command_fail_no_arguments(self):
        with self.assertRaises(CommandError):
            call_command('clearsessions_batch')

    def test_command(self):
        self.assertEqual(Session.objects.all().count(), 90)
        # Running it the first 6 times should clear 10 sessions each time
        for run_count in range(1, 7):
            call_command('clearsessions_batch', '10')
            self.assertEqual(Session.objects.all().count(), 90 - 10 * run_count)
        # The run after that should only clear 1 expired session
        with self.assertRaises(CommandError):
            call_command('clearsessions_batch', '10')

        self.assertEqual(Session.objects.all().count(), 30)
