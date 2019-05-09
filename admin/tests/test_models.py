import datetime

from django.test import TestCase

from admin.models import Program, ClientCustomization


class ProgramTests(TestCase):
    def test_program(self):
        test_json = '{"name": "Maggie","uri": "http://localhost:56480/api/groups/39",' \
                    '"resources": [{"uri": "http://localhost:56480/api/groups/39/users"}, ' \
                    '{"uri": "http://localhost:56480/api/groups/39/groups"}],"data": ' \
                    '{"display_name": "Maggie","start_date": "2014-1-1T00:00:00.00000Z",' \
                    '"end_date": "2014-12-3T00:00:00.00000Z"},"id": 39,"group_type": "series"}'

        test_info = Program(test_json)

        self.assertEqual(test_info.name, "Maggie")
        self.assertEqual(test_info.display_name, "Maggie")
        self.assertEqual(test_info.start_date, datetime.datetime(2014, 1, 1))
        self.assertEqual(test_info.end_date, datetime.datetime(2014, 12, 3))


class AdminClientUITests(TestCase):
    def test_new_ui_is_disabled_by_default(self):
        client_customization = ClientCustomization.objects.create(client_id=100, identity_provider='')
        self.assertTrue(client_customization.new_ui_enabled)
