from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.sessions.models import Session
from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time
from mock import patch, call


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
        with patch('main.management.commands.clearsessions_batch.logger') as mock_log:
            # Running it the first 6 times should clear 10 sessions each time
            for run_count in range(1, 7):
                call_command('clearsessions_batch', '10')
                mock_log.info.assert_has_calls([
                    call('Got batch size of %s', 10),
                    call('Collected %s session ids', 10),
                    call('Collected %s sessions to delete', 10),
                    call('Cleared %s sessions', 10),
                ])
                self.assertEqual(Session.objects.all().count(), 90 - 10 * run_count)
                mock_log.reset_mock()
            # The run after that should only clear 1 expired session
            call_command('clearsessions_batch', '10')
            mock_log.info.assert_has_calls([
                call('Got batch size of %s', 10),
                call('Collected %s session ids', 0),
                call('Collected %s sessions to delete', 0),
                call('Cleared %s sessions', 0),
            ])
            mock_log.warn.assert_called_with("No more sessions to clear")

        self.assertEqual(Session.objects.all().count(), 30)
