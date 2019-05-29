"""
Django management command to clear the session database in batches.
"""

import logging

from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


logger = logging.getLogger(__name__)  # pylint: disable=locally-disabled, invalid-name


class Command(BaseCommand):
    help = "Cleans expired sessions in batches"

    def add_arguments(self, parser):
        parser.add_argument(
            'batch_size',
            type=int,
            help='Number of expired sessions to clear',
        )

    def handle(self, *args, **options):
        session_ids = Session.objects.filter(
            expire_date__lt=timezone.now()
        )[:options['batch_size']].values_list("session_key", flat=True)
        delete_count, _ = Session.objects.filter(pk__in=list(session_ids)).delete()
        logger.info("Cleared %s sessions", delete_count)

        if delete_count < options['batch_size']:
            # Raise error so we know when to switch to the regular clearsessions command
            raise CommandError("No more sessions to clear")
