'''
Error handling for the API client.
'''

import functools
import inspect
import json
import logging
from urllib.error import HTTPError as UrllibHTTPError

from django.utils.translation import ugettext as _
from requests.exceptions import HTTPError as RequestsHTTPError


ERROR_CODE_MESSAGES = {}

log = logging.getLogger(__name__)


class ApiError(Exception):
    '''
    Exception to be thrown when the Api returns an Http error
    '''

    code = 1000  # 1000 represents client-side error, or unknown code
    message = _("Unknown error calling API")
    content_dictionary = {}
    http_error = None
    SENSITIVE_DATA_FIELDS = ["password", "remote_session_key", "session_key"]

    def __init__(self, thrown_error, function_name, error_code_messages=None, **call_context):
        if isinstance(thrown_error, RequestsHTTPError):
            self.code = thrown_error.response.status_code
            self.message = thrown_error.response.reason
            body = thrown_error.response.text
        else:
            # An UrllibHTTPError or a mock of that
            self.code = thrown_error.code
            self.message = thrown_error.reason
            try:
                body = thrown_error.read()
            except (AttributeError, KeyError):
                body = ''

        self.http_error = thrown_error

        self.context = call_context
        self.function_name = function_name

        # does the code have a known reason to be incorrect
        if error_code_messages and self.code in error_code_messages:
            self.message = error_code_messages[self.code]

        # Look in response content for specific message from api response
        try:
            self.content_dictionary = json.loads(body)
        except (ValueError, TypeError):
            self.content_dictionary = {}

        if "message" in self.content_dictionary:
            self.message = self.content_dictionary["message"]

        if "__all__" in self.content_dictionary:
            self.message = self.content_dictionary["__all__"][0]

        super(ApiError, self).__init__()

    def __str__(self):
        self.filter_sensitive_data(self.context)

        argument_list = ', '.join(
            [
                '{}={}'.format(context_name, self.context[context_name])
                for context_name in self.context
            ]
        )
        return "ApiError '{}' ({}) - {}({})".format(
            self.message,
            self.code,
            self.function_name,
            argument_list
        )

    def filter_sensitive_data(self, context):
        for key, value in list(context.items()):
            if isinstance(value, dict):
                self.filter_sensitive_data(value)
            elif key in self.SENSITIVE_DATA_FIELDS:
                context.pop(key, None)


def api_error_protect(func):
    '''
    Decorator which will raise an ApiError for api calls
    '''
    @functools.wraps(func)
    def call_api_method(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (UrllibHTTPError, RequestsHTTPError) as he:
            call_context = {}
            call_context.update(kwargs)
            argument_names = inspect.getargspec(func).args
            for position, arg in enumerate(args):
                if position < len(argument_names):
                    call_context[argument_names[position]] = arg

            api_error = ApiError(
                he,
                func.__name__,
                ERROR_CODE_MESSAGES.get(func.__name__, None),
                **call_context
            )
            log.error("Error calling {}: {}".format(func, api_error))
            raise api_error
    return call_api_method
