from django.utils.translation import ugettext as _

from django.http import HttpResponse, HttpResponseRedirect
from django.middleware import csrf
from forms import LoginForm, RegistrationForm
from api_client import user_api
from remote_auth.models import RemoteUser

from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

from django.contrib import auth
import urllib2 as url_access

import haml_mako.templates as haml


def login(request):
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        form = LoginForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
                request.session["remote_session_key"] = user.session_key
                auth.login(request, user)
                return HttpResponseRedirect('/')  # Redirect after POST
            except url_access.HTTPError, err:
                error = _("An error occurred during login")
                error_messages = {
                    403: _("User account not activated"),
                    401: _("Username or password invalid"),
                }
                if err.code in error_messages:
                    error = error_messages[err.code]
    elif 'username' in request.GET:
        # password fields get cleaned upon rendering the form, but we must
        # provide something here, otherwise the error (password field is
        # required) will appear
        form = LoginForm({"username": request.GET['username'], "password": "fake_password"})
        # set focus to password field
        form.fields["password"].widget.attrs.update({'autofocus': 'autofocus'})
    else:
        form = LoginForm()  # An unbound form
        # set focus to username field
        form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})

    template = haml.get_haml_template('login.html.haml')
    return HttpResponse(template.render_unicode(user=None, form=form, csrf_token=csrf_token(request), error=error))


def logout(request):
    # destory the remote session
    try:
        user_api.delete_session(request.session["remote_session_key"])
    except:
        pass

    # clean user from the local cache
    RemoteUser.remove_from_cache(request.user.id)

    # destroy this session
    auth.logout(request)

    return HttpResponseRedirect('/')  # Redirect after POST


def register(request):
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        form = RegistrationForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                user_api.register_user(request.POST)
                # Redirect after POST
                return HttpResponseRedirect('/login?username=' + request.POST["username"])
            except url_access.HTTPError, err:
                error = _("An error occurred during registration")
                error_messages = {
                    409: _("User with matching username or email already exists")
                }
                if err.code in error_messages:
                    error = error_messages[err.code]
    else:
        form = RegistrationForm()  # An unbound form
        # set focus to username field
        form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})

    template = haml.get_haml_template('register.html.haml')
    return HttpResponse(template.render_unicode(user=None, form=form, csrf_token=csrf_token(request), error=error))


def home(request):
    template_name = 'main.html.haml'
    use_user = None
    if request.user.is_authenticated():
        use_user = request.user

    template = haml.get_haml_template(template_name)
    return HttpResponse(template.render_unicode(user=use_user))


def csrf_token(context):
    """A csrf token that can be included in a form."""
    csrf_token = csrf.get_token(context)
    if csrf_token == 'NOTPROVIDED':
        return ''
    return (u'<div style="display:none"><input type="hidden"'
            ' name="csrfmiddlewaretoken" value="%s" /></div>' % (csrf_token))
