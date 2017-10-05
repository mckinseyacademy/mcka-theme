import inspect
import json
import functools
from urllib2 import HTTPError as Urllib2HTTPError
from requests.exceptions import HTTPError as RequestsHTTPError

from django.utils.translation import ugettext as _


ERROR_CODE_MESSAGES = {}


class ApiError(Exception):
    code = 1000  # 1000 represents client-side error, or unknown code
    message = _("Unknown error calling API")
    content_dictionary = {}
    http_error = None

    '''
    Exception to be thrown when the Api returns an Http error
    '''

    def __init__(self, thrown_error, function_name, error_code_messages=None, **call_context):
        # store the code and
        self.http_error = thrown_error
        self.code = thrown_error.code if hasattr(thrown_error, 'code') else thrown_error.response.status_code

        self.context = call_context
        self.function_name = function_name
        self.message = thrown_error.reason if hasattr(thrown_error, 'reason') else thrown_error.response.reason

        # does the code have a known reason to be incorrect
        if error_code_messages and self.code in error_code_messages:
            self.message = error_code_messages[self.code]

        # Look in response content for specific message from api response
        try:
            self.content_dictionary = json.loads(thrown_error.read())
        except:
            self.content_dictionary = {}

        if "message" in self.content_dictionary:
            self.message = self.content_dictionary["message"]

        if "__all__" in self.content_dictionary:
            self.message = self.content_dictionary["__all__"][0]

        super(ApiError, self).__init__()

    def __str__(self):
        argument_list = ', '.join(
            ['{}={}'.format(
                context_name,
                self.context[context_name]
            )
            for context_name in self.context]
        )
        return "ApiError '{}' ({}) - {}({})".format(
            self.message,
            self.code,
            self.function_name,
            argument_list
        )


def api_error_protect(func):
    '''
    Decorator which will raise an ApiError for api calls
    '''
    @functools.wraps(func)
    def call_api_method(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (Urllib2HTTPError, RequestsHTTPError) as he:
            call_context = {}
            call_context.update(kwargs)
            argument_names = inspect.getargspec(func).args
            for position, arg in enumerate(args):
                call_context[argument_names[position]] = arg
            api_error = ApiError(
                he,
                func.__name__,
                ERROR_CODE_MESSAGES.get(func.__name__, None),
                **call_context
            )
            print "Error calling {}: {}".format(func, api_error)
            raise api_error
    return call_api_method
