import os
import ddt

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import TestCase, RequestFactory
from mock import Mock, patch

from lib.utils import DottableDict
from util.unit_test_helpers import ApplyPatchMixin


@ddt.ddt
class AprosTemplateLoaderTests(TestCase, ApplyPatchMixin):
    def setUp(self):
        self.factory = RequestFactory()

    def mock_request(self, is_authenticated, url, view_name, is_admin):
        request = self.factory.get(url)
        request.user = Mock()
        request.resolver_match = Mock()
        request.user.is_authenticated = is_authenticated
        request.user.is_mcka_admin = is_admin
        request.user.is_internal_admin = is_admin
        request.user.is_mcka_subadmin = is_admin
        request.resolver_match.view_name = view_name
        return request

    @patch('mcka_apros.templates_loaders.thread_local.get_basic_user_data')
    @patch('accounts.middleware.thread_local.get_current_request')
    @ddt.data(
        # For Admin urls it should always load old templates
        ('footer.haml', settings.TEMPLATE_TEST_DIR, '/admin/', 'dummy', True, True, True),
        # For Company Admin urls it should load old template if user is uber admin
        ('footer.haml', settings.TEMPLATE_TEST_DIR, '/admin/company_dashboard', 'company_dashboard',
            True, True, True),
        # For Company Admin urls it should load new template if user is not uber admin
        ('footer.haml', settings.TEMPLATE_NEW_TEST_DIR, '/admin/company_dashboard', 'company_dashboard',
            True, True, False),
        # When new_ui_enabled=False it should load old template
        ('footer.haml', settings.TEMPLATE_TEST_DIR, '/test/', 'dummy', True, False, True),
        # When new_ui_enabled=True it should load new template
        ('footer.haml', settings.TEMPLATE_NEW_TEST_DIR, '/test/', 'dummy', True, True, True),
        # When new_ui_enabled=True but template doesn't exists in new dir
        # It should fall back to old templates
        ('header.haml', settings.TEMPLATE_TEST_DIR, '/test/', 'dummy', True, True, True),
        # When user is not logged in it should load old template
        ('footer.haml', settings.TEMPLATE_TEST_DIR, '/test/', 'dummy', False, True, True),
    )
    @ddt.unpack
    def test_template_exists(self, template_name, template_path, url, view_name, is_authenticated,
                             new_ui_enabled, is_admin, get_current_request, get_basic_user_data):
        get_current_request.return_value = self.mock_request(
            is_authenticated=is_authenticated, url=url, view_name=view_name, is_admin=is_admin
        )
        get_basic_user_data.return_value = DottableDict(new_ui_enabled=new_ui_enabled)

        template = get_template(template_name)
        self.assertEqual(os.path.join(template_path, template_name), str(template.origin.name))

    @patch('mcka_apros.templates_loaders.thread_local.get_basic_user_data')
    @patch('accounts.middleware.thread_local.get_current_request')
    def test_template_not_exists(self, get_current_request, get_basic_user_data):
        get_current_request.return_value = self.mock_request(
            is_authenticated=True, url='/',
            view_name='dummy', is_admin=False
        )
        get_basic_user_data.return_value = DottableDict(new_ui_enabled=False)

        with self.assertRaises(TemplateDoesNotExist):
            get_template('invalid.haml')
