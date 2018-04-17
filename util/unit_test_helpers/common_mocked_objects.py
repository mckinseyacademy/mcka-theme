"""
Common mocked objects and methods for writing unit tests in Apros
"""


class TestUser(object):
    """
    Represents a minimum User object
    """
    id = None
    email = None

    def __init__(self, user_id, email, username='test_user', is_staff=False):
        """
        the plain, old class initializer
        """
        self.id = user_id
        self.email = email
        self.username = username
        self.is_staff = is_staff


def mock_storage_save(storage_obj, name, content, max_length=None):
    """
    Mocked file storage's `save` method. Only returns path and
    does not write any actual file
    """
    return name
