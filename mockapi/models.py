#from django.db import models

import StringIO
import json

# Create your models here.
RESPONSE_DICTIONARY = {}


def _set_dictionary_from_dictionary(dict1, dict2):
    for key in dict1:
        if isinstance(dict1[key], dict):
            dict1[key] = _set_dictionary_from_dictionary(dict1[key], dict2[key])
        else:
            # make sure that it can be set to given value
            dict1[key] = dict2[key]


class MockHttpResponse(object):

    _method = 'GET'
    _response_body = None
    _code = 204
    _address = '/'
    _content_type = None
    _request_format = None

    _next_request_body = False

    def _process_response(self, response_info, remainder):
        self._next_request_body = False

        if len(response_info) < 2:
            raise Exception('Not enough "Response" arguments')

        self._code = int(response_info[1])

        if len(response_info) > 2:
            self._content_type = response_info[2].strip()[1:-1]

    def _process_body(self, body_info, body):
        if self._next_request_body:
            self._request_format = body.strip()
        else:
            self._response_body = body.strip()

    def _process_request(self, request_info, remainder):
        self._next_request_body = True


    def __init__(self, init_data):
# ### GET /api
# + Response 200 (application/json)

#     + Body

#             {
#                 "documentation": "http://docs.openedxapi.apiary.io", 
#                 "name": "Open edX API", 
#                 "uri": "/api", 
#                 "description": "Machine interface for interactions with Open edX."
#                 "resources":[
#                     {
#                         "uri":"/api/groups",
#                         "uri":"/api/sessions",                        
#                         "uri":"/api/system",
#                         "uri":"/api/users",
#                     }
#                 ]
#             }
        try:
            buf = StringIO.StringIO(init_data)
            top_line = buf.readline().strip()
            self._process_top_line(top_line)

            options = buf.read().split('+ ')

            for option in options:
                self._process_option(option.strip())

            is_valid, error = self._is_valid()
            if not is_valid:
                raise Exception("Invalid item = {}\n\n{}".format(error, init_data))

        except Exception, ex:
            print ex.message
            raise ex

    def _process_top_line(self, line_content):
        line_info = line_content[3:].strip().split(' ')
        self._method = line_info[0]
        self._address = line_info[1]

    def _process_option(self, option_info):
        instruction_map = {
            'Response': self._process_response,
            'Body': self._process_body,
            'Request': self._process_request,
        }

        buf = StringIO.StringIO(option_info)
        line_info = buf.readline().strip().split(' ')
        remainder = buf.read()
        processor = instruction_map.get(line_info[0])
        if processor:
            processor(line_info, remainder)

    def _is_valid(self):
        error_message = None
        valid = self._method is not None
        if not valid:
            error_message = "No method given"
        valid = valid and (self._response_body is not None or self._code == 204)
        if not error_message and not valid:
            error_message = "No body given"

        return valid, error_message

    def check_post_format(self, request_body):
        if not self._request_format:
            return True

        desired_format = json.loads(self._request_format)
        given_format = json.loads(request_body)

        try:
            _set_dictionary_from_dictionary(desired_format, given_format)

            # after being updated, the desired format should be the same - otherwise we have something extra, or something missing in given format
            return desired_format == given_format

        except Exception, ex:
            return False

