import ddt

from django.test import TestCase

from util.unit_test_helpers import AprosTestingClient


@ddt.ddt
class TestContextProcessors(TestCase):
    client_class = AprosTestingClient

    def test_program_data_context_processor(self):
        response = self.client.get('/')

        program_context_variables = [
            "current_course", "program", 'feature_flags', 'namespace',
            'course_name', 'client_customization', 'client_nav_links',
            'branding', 'organization_id', 'lesson_custom_label',
            'module_custom_label', 'lessons_custom_label',
            'modules_custom_label'
        ]

        notification_context_variables = [
            'refresh_watcher', 'global_variables',
            'view_audios'
        ]

        for context_variable in program_context_variables + notification_context_variables:
            self.assertIn(context_variable, response.context)

    def test_settings_data_context_processor(self):
        response = self.client.get('/')

        settings_context_variables = [
            'use_i18n', 'ga_tracking_id', 'ta_email_group',
            'ie_favicon_prefix', 'session_id', 'apros_features', 'xblock_theme_css_path',
            'heap_app_id', 'xblock_theme_js_path'
        ]

        for context_variable in settings_context_variables:
            self.assertIn(context_variable, response.context)

    def test_mobile_login_context_processor(self):
        response = self.client.get('/')

        # should not be in context data in normal call
        self.assertNotIn('track_mobile_login', response.context)

        # act as a mobile user agent and check context
        iphone_ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 ' \
                           '(KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'

        response = self.client.get('/', HTTP_USER_AGENT=iphone_ua_string, HTTP_REFERER='http://abc.xyz/login/')

        self.assertIn('track_mobile_login', response.context)

    @ddt.data(
        ('ios', 'user_ios_mobile_app_id'),
        ('android', 'user_android_mobile_app_id')
    )
    @ddt.unpack
    def test_set_mobile_app_id(self, user_agent, expected_context_variable):
        if user_agent == 'ios':
            ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 ' \
                               '(KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
        elif user_agent == 'android':
            ua_string = 'Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP)' \
                    'AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30'
        else:
            ua_string = ''

        response = self.client.get('/', HTTP_USER_AGENT=ua_string)

        self.assertIn(expected_context_variable, response.context)
