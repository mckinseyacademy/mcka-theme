from django.http import HttpResponseRedirect


class AjaxRedirect:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.is_ajax():
            if type(response) == HttpResponseRedirect:
                response.status_code = 278
        return response
