from mock import patch

from lib.utils import DottableDict


class MockedUserDataManager(object):
    def __init__(self, user_id):
        self.user_id = user_id

    def get_basic_user_data(self):
        return DottableDict(
            courses=self.courses if hasattr(self, 'courses') else [],
            current_course=self.current_course if hasattr(self, 'current_course') else None,
            current_program=self.current_program if hasattr(self, 'current_program') else None,
            organization=self.organizations[0] if hasattr(self, 'organizations') and self.organizations else None,
        )


def mock_api_data_manager(module_path, data={}):
    patch(module_path, new=MockedUserDataManager).start()

    for key, value in data.iteritems():
        setattr(MockedUserDataManager, key, value)
