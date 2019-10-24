from django.core.management.base import BaseCommand
import re

from admin.models import DeletionAdmin


class Command(BaseCommand):
    help = """'add' or 'remove' emails to be cc'ed on bulk/company deletion"""
    rx = re.compile(r'^[\w._+\-]+@\w+\.\w{2,3}')  # test.test+test_test-test@test.com

    def add_arguments(self, parser):
        parser.add_argument('op', nargs=1, type=str, help='"add" or "remove"')
        parser.add_argument('email', nargs='+', type=str, help='Deletion admin email')

    @staticmethod
    def add(emails):
        return [DeletionAdmin.objects.get_or_create(email=email) for email in emails]

    @staticmethod
    def remove(emails):
        return DeletionAdmin.objects.filter(email__in=emails).delete()

    def handle(self, *args, **options):
        try:
            op = options['op'][0]
            emails = options['email']
            if op.lower() not in ['add', 'remove']:
                raise Exception("Only 'add' and 'remove' operations supported")
            if not all([self.rx.match(email) for email in emails]):
                raise Exception("At least one email failed validation")
        except Exception as e:
            self.stderr.write(self.style.ERROR('Task failed to trigger with exception: "%s"' % str(e)))
        else:
            if op.lower() == 'add':
                return str(self.add(emails))
            return str(self.remove(emails))
