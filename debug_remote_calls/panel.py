import functools
import json
import threading
import time
import urllib.request
import urllib.error
import urllib.parse
from io import StringIO
from urllib.response import addinfourl

from debug_toolbar.panels import Panel
from django.conf import settings
from requests import Session


threadlocal = threading.local()
threadlocal.api_calls = []

_original_request = Session.request


def _now_in_ms():
    return int(round(time.time() * 1000))


@functools.wraps(_original_request)
def _request(self, method, url, **kwargs):
    start_time = _now_in_ms()
    response = _original_request(self, method, url, **kwargs)
    threadlocal.api_calls = getattr(threadlocal, 'api_calls', [])

    threadlocal.api_calls.append({
        'request': {
            'method': method,
            'url': url,
            'headers': getattr(self, 'headers', {}),
            'data': kwargs.get('data', {}),
            'duration': _now_in_ms() - start_time,
        },
        'response': {
            'code': response.status_code,
            'size': len(response.content),
            'headers': response.headers,
            'data': response.content,
        }
    })
    return response


class DebugHandler(urllib.request.HTTPHandler):

    def http_request(self, request):
        request.start_time = _now_in_ms()
        return request

    def http_response(self, request, response):
        # read the response data
        data = response.read().decode('utf-8')
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
                'data': request.data,
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


class DebugRemoteCalls(Panel):
    template = 'panel.html'
    has_content = True

    def title(self):
        return 'Remote Calls'

    def nav_subtitle(self):
        return "{} calls in {}ms".format(self.call_count(), self.total_time())

    def process_request(self, request):
        threadlocal.api_calls = []
        opener = urllib.request.build_opener(DebugHandler)
        urllib.request.install_opener(opener)

        if settings.DEBUG and Session.request != _request:
            Session.request = _request

        response = super(DebugRemoteCalls, self).process_request(request)
        if settings.DEBUG and Session.request == _request:
            Session.request = _original_request

        self.record_stats({
            'call_count': self.call_count(),
            'api_calls': threadlocal.api_calls
        })

        return response

    def total_time(self):
        time = 0
        for call in threadlocal.api_calls:
            time = time + call['request']['duration']
        return time

    def call_count(self):
        return len(threadlocal.api_calls)
