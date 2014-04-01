''' views for auth, sessions, users '''
from django.utils.translation import ugettext as _

from django.http import HttpResponse, HttpResponseRedirect
from django.middleware import csrf
from mcka_apros.forms import LoginForm, RegistrationForm
from api_client import user_api
from accounts.models import RemoteUser

from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

from django.contrib import auth
import urllib2 as url_access

from django.shortcuts import render

import urlparse

from courses.views import homepage

from django.contrib.auth.decorators import login_required


def _get_qs_value_from_url(value_name, url):
    ''' gets querystring value from url that contains a querystring '''
    parsed_url = urlparse.urlparse(url)
    query_strings = urlparse.parse_qs(parsed_url.query)
    if value_name in query_strings and len(query_strings[value_name]) > 0:
        return query_strings[value_name][0]
    return None


def login(request):
    ''' handles requests for login form and their submission '''
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        form = LoginForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                user = auth.authenticate(
                    username=request.POST['username'],
                    password=request.POST['password']
                )
                request.session["remote_session_key"] = user.session_key
                auth.login(request, user)

                redirect_to = _get_qs_value_from_url(
                    'next',
                    request.META['HTTP_REFERER']
                ) if 'HTTP_REFERER' in request.META else None
                if not redirect_to:
                    redirect_to = '/'

                return HttpResponseRedirect(redirect_to)  # Redirect after POST
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
        form = LoginForm(
            {"username": request.GET['username'], "password": "fake_password"}
        )
        # set focus to password field
        form.fields["password"].widget.attrs.update({'autofocus': 'autofocus'})
    else:
        form = LoginForm()  # An unbound form
        # set focus to username field
        form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "user": None,
        "form": form,
        "error": error,
        "login_label": _("Log In"),
        }
    return render(request, 'accounts/login.html.haml', data)


def logout(request):
    ''' handles requests to logout '''
    # destory the remote session, protect against bad API response, still want
    # our local stuff to go
    try:
        user_api.delete_session(request.session["remote_session_key"])
    except url_access.HTTPError:
        pass

    # clean user from the local cache
    RemoteUser.remove_from_cache(request.user.id)

    # destroy this session
    auth.logout(request)

    return HttpResponseRedirect('/')  # Redirect after POST


def register(request):
    ''' handles requests for registration form and their submission '''
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        form = RegistrationForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                user_api.register_user(request.POST)
                # Redirect after POST
                return HttpResponseRedirect(
                    '/accounts/login?username={}'.format(
                        request.POST["username"]
                    )
                )
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

    data = {
        "user": None,
        "form": form,
        "error": error,
        "register_label": _("Register"),
        }
    return render(request, 'accounts/register.html.haml', data)


def home(request):
    ''' show me the home page '''

    # if we have an authenticated user, show them their course-based homepage
    if request.user and request.user.is_authenticated():
        return homepage(request)

    return render(request, 'main.html.haml', {"user": None})


@login_required
def user_profile(request):
    ''' gets user_profile information in html snippet '''
    user = user_api.get_user(request.user.id)
    user_data = {
        "user_image_url": user.image_url(160),
        "user_formatted_name": user.formatted_name(),
        "user_email": user.email,
    }
    return render(request, 'accounts/user_profile.html.haml', user_data)
