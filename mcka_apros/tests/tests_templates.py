import os
import ddt

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import TestCase, RequestFactory
from mock import Mock, patch

from util.unit_test_helpers import ApplyPatchMixin


@ddt.ddt
class AprosTemplateLoaderTests(TestCase, ApplyPatchMixin):
    def setUp(self):
        self.factory = RequestFactory()

    def mock_request(self, is_authenticated, url, view_name):
        request = self.factory.get(url)
        request.user = Mock(is_authenticated=is_authenticated)
        request.resolver_match = Mock(view_name=view_name)
        return request

    @patch('mcka_apros.templates_loaders.get_customization')
    @patch('accounts.middleware.thread_local.get_current_request')
    @ddt.data(
        # For Admin urls it should always load old templates
        ('footer.haml', settings.TEMPLATE_TEST_DIR, '/admin/', 'dummy', True, True),
        # For Company Admin urls it should load new template
        ('footer.haml', settings.TEMPLATE_NEW_TEST_DIR, '/admin/company_dashboard', 'company_dashboard', True, True),
        # When new_ui_enabled=False it should load old template
        ('footer.haml', settings.TEMPLATE_TEST_DIR, '/test/', 'dummy', True, False),
        # When new_ui_enabled=True it should load new template
        ('footer.haml', settings.TEMPLATE_NEW_TEST_DIR, '/test/', 'dummy', True, True),
        # When new_ui_enabled=True but template doesn't exists in new dir
        # It should fall back to old templates
        ('header.haml', settings.TEMPLATE_TEST_DIR, '/test/', 'dummy', True, True),
        # When user is not logged in it should load old template
        ('footer.haml', settings.TEMPLATE_TEST_DIR, '/test/', 'dummy', False, True),
    )
    @ddt.unpack
    def test_template_exists(self, template_name, template_path, url, view_name, is_authenticated, new_ui_enabled,
                             get_current_request, get_customizations):
        get_current_request.return_value = self.mock_request(
            is_authenticated=is_authenticated, url=url, view_name=view_name
        )
        get_customizations.return_value = Mock(new_ui_enabled=new_ui_enabled)

        template = get_template(template_name)
        self.assertEqual(os.path.join(template_path, template_name), str(template.origin.name))

    @patch('mcka_apros.templates_loaders.get_customization')
    @patch('accounts.middleware.thread_local.get_current_request')
    def test_template_not_exists(self, get_current_request, get_customizations):
        get_current_request.return_value = self.mock_request(is_authenticated=True, url='/', view_name='dummy')
        get_customizations.return_value = Mock(new_ui_enabled=False)

        with self.assertRaises(TemplateDoesNotExist):
            get_template('invalid.haml')
