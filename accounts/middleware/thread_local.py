''' globally available request object  '''
import threading

_threadlocal = threading.local()


class ThreadLocal(object):

    def process_request(self, request):
        _threadlocal.request = request
        _threadlocal.current_course = None
        _threadlocal.static_tabs = None

    def process_response(self, request, response):
        _threadlocal.request = None
        _threadlocal.current_course = None
        _threadlocal.static_tabs = None
        return response


def get_current_request():
    return getattr(_threadlocal, 'request', None)


def set_course_context(course, depth):
    setattr(_threadlocal, 'current_course', {
            "course_id": course.id,
            "course_content": course,
            "depth": depth
        }
    )


def get_course_context():
    return getattr(_threadlocal,  'current_course', None)

def set_static_tab_context(static_tab_dictionary, name=None):
    if name:
        static_tabs = get_static_tab_context()
        if not static_tabs:
            static_tabs = []
        static_tabs[name] = static_tab_dictionary
        setattr(_threadlocal, 'static_tabs', static_tabs)
    else:
        setattr(_threadlocal, 'static_tabs', static_tab_dictionary)

def get_static_tab_context(name=None, tab_id=None):
    if name:
        static_tabs = getattr(_threadlocal, 'static_tabs', None)
        if name in static_tabs.keys():
            return static_tabs[name]
        return None
    return getattr(_threadlocal, 'static_tabs', None)
