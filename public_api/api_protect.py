import json

from functools import wraps
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound

from .models import ApiToken
from admin.models import Client

def api_json_response(func):
    '''
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    '''
    def decorator(request, *args, **kwargs):
        print "\n\n====JSON======="
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = json.dumps(objects)
            if 'callback' in request.REQUEST:
                # a jsonp response!
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                return HttpResponse(data, "text/javascript")
        except:
            data = json.dumps(str(objects))
        return HttpResponse(data, "application/json")
    return decorator

def api_authenticate_protect(func):
    '''
    Decorator to protect API calls with an auth token
    '''
    @wraps(func)
    def _wrapped(request, *args, **kwargs):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if 'token' in auth:
            try:
                organization = ApiToken.objects.get(token = auth.split()[1])
                if organization:
                    request.organization = organization
                    return func(request, *args, **kwargs)
            except:
                return HttpResponseForbidden()
        return HttpResponseForbidden()
    return _wrapped

def api_user_protect(func):
    '''
    Decorator to fetch user by email
    '''
    @wraps(func)
    def _wrapped(request, *args, **kwargs):
        email = request.META.get('HTTP_X_EMAIL', '')
        data = {
            "email": email,
            "error": _("Missing email"),
        }
        if email:
            client = Client.fetch(request.organization.client_id)
            students = client.fetch_students_by_enrolled()

            try:
                request.user = [student for student in students if student.email == email][0]
                return func(request, *args, **kwargs)
            except:
                data['error'] = _("User not found")
                return HttpResponse(json.dumps(data), 'application/json', 400)
        return HttpResponse(json.dumps(data), 'application/json', 400)
    return _wrapped
