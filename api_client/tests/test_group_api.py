import mock
from datetime import datetime

from django.test import TestCase

from api_client.group_models import GroupInfo
from util.unit_test_helpers import ApplyPatchMixin


class TestGroupInfo(GroupInfo):
    data_fields = ["display_name", "interests", "birth_date", "start_date", "end_date"]
    group_type = "test_group"
    date_fields = ["birth_date", "start_date", "end_date"]


class TestGroupInfoTest(TestCase, ApplyPatchMixin):
    def setUp(self):
        mock_group_api = self.apply_patch('api_client.group_models.group_api')
        mock_group_api.create_group.return_value = mock.Mock(id=1)
        fetch_group_response = mock.Mock(display_name='A Test Group', birth_date=datetime(1968, 1, 31))
        fetch_group_response.name = 'a_test_group'
        mock_group_api.fetch_group.return_value = fetch_group_response

    def test_group_info(self):
        test_info = TestGroupInfo.create("a_test_group", {"display_name": "A Test Group", "birth_date_year": 1968,
                                                          "birth_date_month": 1, "birth_date_day": 31})

        # API only returns simple group info, not including data, so we fetch
        stored_test_info = TestGroupInfo.fetch(test_info.id)

        self.assertEqual(stored_test_info.name, "a_test_group")
        self.assertEqual(stored_test_info.display_name, "A Test Group")
        self.assertEqual(stored_test_info.birth_date, datetime(1968, 1, 31))

    def test_full_info_response(self):
        test_json = '{"name": "Maggie","uri": "http://localhost:56480/api/groups/39","resources": [{' \
                    '"uri": "http://localhost:56480/api/groups/39/users"}, {"uri": "http://localhost:56480/api/' \
                    'groups/39/groups"}],"data": {"display_name": "Maggie","start_date": "2014-1-1T00:00:00.00000Z",' \
                    '"end_date": "2014-12-3T00:00:00.00000Z"},"id": 39,"group_type": "series"}'

        test_info = TestGroupInfo(test_json)

        self.assertEqual(test_info.name, "Maggie")
        self.assertEqual(test_info.display_name, "Maggie")
        self.assertEqual(test_info.start_date, datetime(2014, 1, 1))
        self.assertEqual(test_info.end_date, datetime(2014, 12, 3))
