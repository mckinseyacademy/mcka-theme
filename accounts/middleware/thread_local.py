''' globally available request object  '''
import threading

_threadlocal = threading.local()


class ThreadLocal(object):

    def process_request(self, request):
        _threadlocal.request = request


def get_current_request():
    return getattr(_threadlocal, 'request', None)
