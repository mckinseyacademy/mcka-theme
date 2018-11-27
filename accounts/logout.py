from django.http import HttpResponseRedirect
from django.contrib import auth

from api_client.api_error import ApiError
from api_client import user_api

from .models import RemoteUser


def logout(request):
    ''' handles requests to logout '''
    # destory the remote session, protect against bad API response, still want
    # our local stuff to go
    try:
        user_api.delete_session(request.session.get("remote_session_key"))
    except ApiError:
        pass

    # clean user from the local cache
    try:
        RemoteUser.remove_from_cache(request.user.id)
    except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
        pass

    # destroy this session
    try:
        auth.logout(request)
    except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
        pass

    return HttpResponseRedirect('/')  # Redirect after POST
