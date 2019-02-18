''' globally available request object  '''
import threading

_threadlocal = threading.local()


class ThreadLocal(object):

    def process_request(self, request):
        _threadlocal.request = request
        _threadlocal.current_course = None
        _threadlocal.static_tabs = None
        _threadlocal.user_permissions = None

    def process_response(self, request, response):
        _threadlocal.request = None
        _threadlocal.current_course = None
        _threadlocal.static_tabs = None
        _threadlocal.user_permissions = None
        return response


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
