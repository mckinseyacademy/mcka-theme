''' globally available request object  '''
import threading

_threadlocal = threading.local()


class ThreadLocal(object):

    def process_request(self, request):
        _threadlocal.request = request


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
