''' globally available request object  '''
import threading

from api_data_manager.user_data import UserDataManager


_threadlocal = threading.local()


class ThreadLocal:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _threadlocal.request = request
        _threadlocal.current_course = None
        _threadlocal.static_tabs = None
        _threadlocal.user_permissions = None
        _threadlocal.users_data = {}

        response = self.get_response(request)
        _threadlocal.request = None
        _threadlocal.current_course = None
        _threadlocal.static_tabs = None
        _threadlocal.user_permissions = None
        _threadlocal.users_data = {}
        return response


def get_basic_user_data(user_id):
    user_data = _threadlocal.users_data.get(user_id, None)
    if user_data is None:
        user_data = UserDataManager(user_id=user_id).get_basic_user_data()
        _threadlocal.users_data[user_id] = user_data

    return user_data


def get_current_request():
    return getattr(_threadlocal, 'request', None)


def set_static_tab_context(course_tabs):
    setattr(_threadlocal, 'course_tabs', course_tabs)


def get_static_tab_context():
    return getattr(_threadlocal, 'course_tabs', None)


def set_user_permissions_context(permissions=None):
    if permissions:
        setattr(_threadlocal, 'user_permissions', permissions)
    else:
        setattr(_threadlocal, 'user_permissions', None)


def get_user_permissions_context():
    return getattr(_threadlocal, 'user_permissions', None)
