import ddt

from django.core import mail
from django.test import TestCase

from util.email_helpers import send_html_email
from util.unit_test_helpers import ApplyPatchMixin
from api_client.user_models import UserResponse


@ddt.ddt
class TestEmailMethods(TestCase, ApplyPatchMixin):
    """
    Test the email utility methods
    """
    def setUp(self):
        super(TestEmailMethods, self).setUp()

        user_api = self.apply_patch('admin.tasks.user_api')
        user_api.get_user.return_value = UserResponse(dictionary={
            "id": 1,'username': 'user1', 'email': 'user@exmple.com', 'first_name': 'Test User', 'is_active': True
        })

    @ddt.data(
        (['test@example.org'], 'admin/export_stats_email_template.haml', True),
        ([], 'admin/export_stats_email_template.haml', False),
        (['test@example.org'], '', False),
    )
    @ddt.unpack
    def test_send_html_email(self, to_emails, template_name, valid_data):
        if valid_data:
            send_html_email(
                to_emails=to_emails,
                template_name=template_name
            )
            self.assertEqual(len(mail.outbox), 1)
        else:
            with self.assertRaises(ValueError):
                send_html_email(
                    to_emails=to_emails,
                    template_name=template_name
                )
