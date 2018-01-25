from django.http import HttpResponse
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import MockHttpResponse

BASE_MOCK_RESPONSE = '### GET /mockapi\n+ Response 200\n    + Body\n            {"mock_api":"uninitialised"}'
MOCK_NOT_FOUND_RESPONSE = '### GET /mockapi\n+ Response 404\n    + Body\n            {"mock_api":"mock path not found"}'

class MockResponseView(View):
    mock_responses = [MockHttpResponse(BASE_MOCK_RESPONSE)]

    def _select_response(self, request, url_args):
        for mr in self.mock_responses:
            if mr._method == request.method:
                return mr

        return MockHttpResponse(MOCK_NOT_FOUND_RESPONSE)

    def _return_mock_content(self, request, *args, **kwargs):
        arg_list = ""
        for myarg in kwargs:
            arg_list += ", {} = {}".format(myarg, kwargs[myarg])
        print "Mocking API response with arguments {}".format(arg_list)
        mock_response_object = self._select_response(request, kwargs)

        print "Matched path with {}".format(mock_response_object._address)

        fixed_content = mock_response_object._response_body.replace('http://openedxapi.apiary-mock.com/', request.build_absolute_uri('/mockapi/'))

        content_type = "application/json"
        if mock_response_object._content_type:
            content_type = mock_response_object._content_type

        response_kwargs = {
            "content_type": content_type,
            "status": mock_response_object._code,
        }
        return HttpResponse(content=fixed_content, **response_kwargs)

    def get(self, request, *args, **kwargs):
        return self._return_mock_content(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._return_mock_content(request, *args, **kwargs)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(MockResponseView, self).dispatch(*args, **kwargs)
