import json
import re

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
                token = re.search(r'[\w]{64}', auth).group(0)
                organization = ApiToken.objects.get(token = token)
                if organization:
                    request.organization = organization
                    return func(request, *args, **kwargs)
                else:
                    data = {"error": _("Client not found")}
                    return HttpResponse(json.dumps(data), 'application/json', 401)
            except:
                data = {"error": _("Token or Client not found")}
                return HttpResponse(json.dumps(data), 'application/json', 401)
        data = {"error": _("Token missing")}
        return HttpResponse(json.dumps(data), 'application/json', 401)
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
                user = next((student for student in students if student.email.lower() == email.lower()), None)
                if user:
                    request.user = user
                    return func(request, *args, **kwargs)
                else:
                    data['error'] = _("User not found")
                    return HttpResponse(json.dumps(data), 'application/json', 400)
            except:
                data['error'] = _("User not found")
                return HttpResponse(json.dumps(data), 'application/json', 400)
        return HttpResponse(json.dumps(data), 'application/json', 400)
    return _wrapped
