from debug_toolbar.panels import DebugPanel
import urllib2
from urllib import addinfourl
from StringIO import StringIO
import json

api_calls = []


class DebugHandler(urllib2.HTTPHandler):

    def http_response(self, request, response):
        global api_calls

        # read the response data
        data = response.read()
        size = len(data)

        # pretty print JSON
        if 'json' in response.headers.get('Content-Type', ''):
            data = json.dumps(json.loads(data),
                              indent=4, separators=(',', ': '))

        api_calls.append({
            'request': {
                'method': request.get_method(),
                'url': request.get_full_url(),
                'headers': request.headers,
                'data': request.get_data(),
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
        return "{} remote calls".format(self.call_count())

    def process_request(self, request):
        global api_calls
        api_calls = []
        opener = urllib2.build_opener(DebugHandler)
        urllib2.install_opener(opener)

    def process_response(self, request, response):
        self.record_stats({
            'call_count': self.call_count(),
            'api_calls': api_calls
        })

    def call_count(self):
        return len(api_calls)
