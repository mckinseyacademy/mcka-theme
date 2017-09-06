from django.test import TestCase

from api_data_manager.user_data import UserDataManager
from accounts.helpers import TestUser

from api_client import user_api



class TestUserDataManager(TestCase):
    def setUp(self):
        pass

    def test_user_groups(self):
        data = user_api.get_user_groups(6, parse_object=None)
        UserDataManager.flush_cache()
