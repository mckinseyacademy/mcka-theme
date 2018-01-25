from debug_toolbar.panels import DebugPanel
import urllib2
from urllib import addinfourl
from StringIO import StringIO
import json
import threading
import time


threadlocal = threading.local()
threadlocal.api_calls = []


def _now_in_ms():
    return int(round(time.time() * 1000))


class DebugHandler(urllib2.HTTPHandler):

    def http_request(self, request):
        request.start_time = _now_in_ms()
        return request

    def http_response(self, request, response):
        # read the response data
        data = response.read()
        size = len(data)

        # pretty print JSON
        if 'json' in response.headers.get('Content-Type', ''):
            data = json.dumps(json.loads(data),
                              indent=4, separators=(',', ': '))

        # if we're in a different thread, api_calls doesn't exist
        threadlocal.api_calls = getattr(threadlocal, 'api_calls', [])

        threadlocal.api_calls.append({
            'request': {
                'method': request.get_method(),
                'url': request.get_full_url(),
                'headers': request.headers,
                'data': request.get_data(),
                'duration': _now_in_ms() - request.start_time,
            },
            'response': {
                'code': response.code,
                'size': size,
                'headers': response.headers,
                'data': data,
            }
        })

        # recreate the response object (with buffered data)
        resp = addinfourl(StringIO(data), response.headers,
                          response.url, response.code)
        resp.msg = response.msg
        return resp


class DebugRemoteCalls(DebugPanel):

    template = 'panel.html'
    has_content = True

    def title(self):
        return 'Remote Calls'

    def nav_subtitle(self):
        return "{} calls in {}ms".format(self.call_count(), self.total_time())

    def process_request(self, request):
        threadlocal.api_calls = []
        opener = urllib2.build_opener(DebugHandler)
        urllib2.install_opener(opener)

    def process_response(self, request, response):
        self.record_stats({
            'call_count': self.call_count(),
            'api_calls': threadlocal.api_calls
        })

    def total_time(self):
        time = 0
        for call in threadlocal.api_calls:
            time = time + call['request']['duration']
        return time

    def call_count(self):
        return len(threadlocal.api_calls)
