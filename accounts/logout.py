
from django.http import HttpResponseRedirect
from django.contrib import auth
from api_client import user_api
from .models import RemoteUser
import urllib2 as url_access

def logout(request):
    ''' handles requests to logout '''
    # destory the remote session, protect against bad API response, still want
    # our local stuff to go
    try:
        user_api.delete_session(request.session.get("remote_session_key"))
    except url_access.HTTPError:
        pass

    # clean user from the local cache
    RemoteUser.remove_from_cache(request.user.id)

    # destroy this session
    auth.logout(request)

    return HttpResponseRedirect('/')  # Redirect after POST
