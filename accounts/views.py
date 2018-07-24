''' views for auth, sessions, users '''
import base64
import hashlib
import hmac
import json
import os
import random
import urlparse
from urllib import urlencode, quote
import datetime
import math
import logging
import string
import re
import requests
import StringIO

from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_slug
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseBadRequest, HttpResponseForbidden,
                         HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse)
from django.contrib import auth, messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.forms.widgets import HiddenInput
from django.views.decorators.cache import never_cache
from django.template.loader import render_to_string
from requests import ConnectionError, HTTPError

from util.url_helpers import get_referer_from_request
from courses.models import FeatureFlags
from api_client import user_api, course_api
from api_client.json_object import JsonObjectWithImage
from api_client.api_error import ApiError
from api_client import platform_api
from api_client import http_request_methods
from mcka_apros.settings import COOKIES_YEARLY_EXPIRY_TIME, LANGUAGES
from mobile_apps.controller import get_mobile_app_download_popup_data

from admin.models import Client, Program, LearnerDashboard, CourseRun, SelfRegistrationRoles
from admin.controller import load_course
from admin.models import AccessKey, ClientCustomization, OTHER_ROLE
from courses.user_courses import standard_data, get_current_course_for_user, get_current_program_for_user, \
    CURRENT_PROGRAM, set_current_course_for_user
from lib.context_processors import add_edx_notification_context
from util.i18n_helpers import set_language

from .models import RemoteUser, UserActivation, UserPasswordReset, PublicRegistrationRequest
from .controller import (
    user_activation_with_data, ActivationError, is_future_start, get_sso_provider,
    process_access_key, process_registration_request, _process_course_run_closed, _set_number_of_enrolled_users,
    send_warning_email_to_admin, append_user_mobile_app_id_cookie
)
from util.user_agent_helpers import is_mobile_user_agent
from .forms import (
    LoginForm, ActivationForm, FinalizeRegistrationForm, FpasswordForm, SetNewPasswordForm, UploadProfileImageForm,
    EditFullNameForm, EditTitleForm, SSOLoginForm, ActivationFormV2, PublicRegistrationForm,
    LoginIdForm)
from django.shortcuts import resolve_url
from django.utils.http import urlsafe_base64_decode
from django.utils.dateformat import format
from django.template.response import TemplateResponse

import logout as logout_handler

from django.contrib.auth.views import password_reset_done, password_reset_complete
from django.core.urlresolvers import reverse, resolve, Resolver404
from admin.views import ajaxify_http_redirects

log = logging.getLogger(__name__)

VALID_USER_FIELDS = ["email", "first_name", "last_name", "full_name", "city", "country", "username", "password", "is_active", "title", "profile_image"]
USERNAME_INVALID_CHARS_REGEX = re.compile("[^-\w]")

LOGIN_MODE_COOKIE = 'login_mode'
MOBILE_URL_SCHEME_COOKIE = 'mobile_url_scheme'
SSO_ACCESS_KEY_SESSION_ENTRY = 'sso_access_key_id'
SSO_AUTH_ENTRY = 'apros'

MISSING_ACCESS_KEY_ERROR = _("Your login did not match any known accounts, a registration key is required "
                             "in order to create a new account.")
CANT_PROCESS_ACCESS_KEY = _("There was an error enrolling you in a course using the registration key you provided")

OAUTH2_AUTHORIZE_PATH = '/oauth2/authorize/'
OAUTH2_ACCESS_TOKEN_PATH = '/oauth2/access_token/'


def _get_qs_value_from_url(value_name, url):
    ''' gets querystring value from url that contains a querystring '''
    parsed_url = urlparse.urlparse(url)
    query_strings = urlparse.parse_qs(parsed_url.query)
    if value_name in query_strings and len(query_strings[value_name]) > 0:
        return query_strings[value_name][0]
    return None

def _validate_path(redirect_to):
    ''' prevent attacker controllable redirection to third-party applications '''
    if redirect_to is None:
        return

    # resolver expects a trailing slash
    if redirect_to[-1] != '/':
        redirect_to += '/'
    try:
        resolve(redirect_to)
    except Resolver404:
        logger = logging.getLogger(__name__)
        logger.error('Invalid Redirect: {}'.format(redirect_to))
        raise

def _get_stored_image_url(request, image_url):
    if image_url[:10] == '/accounts/':
        return image_url[10:]
    elif image_url[:8] == '/static/':
        prefix = 'https://' if request.is_secure() else 'http://'
        return prefix + request.host() + image_url
    return image_url


def _get_redirect_to(request):
    redirect_to = request.GET.get('next', None)

    if not redirect_to and 'HTTP_REFERER' in request.META:
        redirect_to = _get_qs_value_from_url('next', request.META['HTTP_REFERER'])

    return redirect_to


def _build_sso_redirect_url(provider, next):
    """
    Builds redirect url for SSO login/registration

    Args:
        * provider: str - IdP slug as configured in LMS admin
        * next: str - URL to redirect after successful authentication; can be relative since we assume the LMS and
                      Apros are on the same domain (providing absolute might cause redirect to be ignored due to
                      redirect sanitization in python-saml)
    """
    query_args = {'auth_entry': SSO_AUTH_ENTRY, 'next': next, 'idp': provider}
    return '{lms_auth}login/tpa-saml/?{query}'.format(lms_auth=settings.LMS_AUTH_URL, query=urlencode(query_args))


def _get_redirect_to_current_course(request):
    course_id = get_current_course_for_user(request)
    future_start_date = False

    if course_id:
        course = course_api.get_course(course_id=course_id, depth=0)
        if hasattr(course, 'start'):
            future_start_date = is_future_start(course.start)
        else:
            program = get_current_program_for_user(request)

            for program_course in program.courses:
                if program_course.id == course_id:
                    if hasattr(program, 'start_date') and future_start_date is False:
                        future_start_date = is_future_start(program.start_date)

    if course_id and not future_start_date:
        return reverse('course_landing_page', kwargs=dict(course_id=course_id))
    return reverse('protected_home')


def _process_authenticated_user(request, user, activate_account=False):
    redirect_to = _get_redirect_to(request)
    _validate_path(redirect_to)

    request.session["remote_session_key"] = user.session_key
    auth.login(request, user)

    if SSO_ACCESS_KEY_SESSION_ENTRY in request.session:
        try:
            access_key, client = _get_access_key(request.session[SSO_ACCESS_KEY_SESSION_ENTRY])
        except (AccessKey.DoesNotExist, AttributeError, IndexError):
            messages.error(request, CANT_PROCESS_ACCESS_KEY)
        else:
            _process_access_key_and_remove_from_session(request, user, access_key, client)

    if not redirect_to:
        redirect_to = _get_redirect_to_current_course(request)
    if activate_account:
        redirect_to += '?username={}'.format(user.username)
    response = HttpResponseRedirect(redirect_to)  # Redirect after POST
    if 'remote_session_key' in request.session:
        response.set_cookie(
            'sessionid',
            request.session["remote_session_key"],
            domain=settings.LMS_SESSION_COOKIE_DOMAIN,
        )
    if hasattr(user, 'csrftoken'):
        response.set_cookie(
            'csrftoken',
            user.csrftoken,
        )

    return response


def _process_access_key_and_remove_from_session(request, user, access_key, client):
    if SSO_ACCESS_KEY_SESSION_ENTRY in request.session:
        del request.session[SSO_ACCESS_KEY_SESSION_ENTRY]
    process_access_key_result = process_access_key(user, access_key, client)
    for message_level, message in process_access_key_result.messages:
        messages.add_message(request, message_level, message)

    # cleaning up current program session-cached value
    if CURRENT_PROGRAM in request.session:
        del request.session[CURRENT_PROGRAM]

    if process_access_key_result.enrolled_in_course_ids:
        current_course_id = process_access_key_result.enrolled_in_course_ids[0]
        set_current_course_for_user(request, current_course_id)


def _get_access_key(key_code):
    access_key = AccessKey.objects.get(code=key_code)
    client = Client.fetch(access_key.client_id)
    return access_key, client


def _append_login_mode_cookie(response, login_mode):
    response.set_cookie(
        LOGIN_MODE_COOKIE, login_mode, expires=COOKIES_YEARLY_EXPIRY_TIME
    )


def _append_mobile_url_scheme_cookie(response, mobile_url_scheme):
    response.set_cookie(
        MOBILE_URL_SCHEME_COOKIE, mobile_url_scheme, expires=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    )


def _expire_session_cookies(response):
    expire_in_past = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    response.set_cookie('sessionid', 'to-delete', domain=settings.LMS_SESSION_COOKIE_DOMAIN, expires=expire_in_past)
    response.set_cookie('csrftoken', 'to-delete', expires=expire_in_past)


def _get_mobile_url_scheme(request):
    return request.GET.get(
        'mobile_url_scheme',
        request.COOKIES.get(MOBILE_URL_SCHEME_COOKIE, None))


def _build_mobile_redirect_response(request, data):
    ''' Builds a redirect response (via an HTML page) for mobile platforms. '''
    scheme = _get_mobile_url_scheme(request)
    redirect_url = '{scheme}://{path}?{query}'.format(
        scheme=scheme,
        path=settings.MOBILE_SSO_PATH,
        query=urlencode(data))
    return render(request, 'accounts/oauth_mobile_redirect.haml', {'redirect_to': redirect_url})


def login(request):
    ''' handles requests for login form and their submission '''
    request.session['ddt'] = False  # Django Debug Tool session key init.

    # Redirect IE to home page, login not available
    if request.META.has_key('HTTP_USER_AGENT'):
        ua = request.META['HTTP_USER_AGENT'].lower()
        if re.search('msie [1-8]\.', ua):
            return HttpResponseRedirect('/')

    if request.method == 'POST':  # If the form has been submitted...
        return login_post_view(request)

    elif request.method == 'GET':
        return login_get_view(request)

    return HttpResponseNotAllowed(permitted_methods=('GET', 'POST'))


def login_get_view(request):
    error = None
    data = {}

    login_mode = request.COOKIES.get(LOGIN_MODE_COOKIE, 'normal')
    # Get the query param if user is already activated
    account_activate_check = request.GET.get('account_activate_check', None)

    if 'sessionid' in request.COOKIES:
        # The user may already be logged in to the LMS.
        # (e.g. they used the LMS's third_party_auth to authenticate, then got redirected back here)
        try:
            user = auth.authenticate(remote_session_key=request.COOKIES['sessionid'])
            if user:
                response = _process_authenticated_user(request, user)
                _append_login_mode_cookie(response, login_mode)
                append_user_mobile_app_id_cookie(response, user.id)
                return response
        except ApiError as err:
            error = err.message

    form = LoginForm()
    # set focus to username field
    form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})

    if 'reset' in request.GET:
        form.reset = request.GET['reset']

    if account_activate_check:
        data["activation_message"] = _("Your account has already been activated. Please enter credentials to login")

    data["user"] = None
    data["form"] = form or LoginForm()
    data["login_mode"] = login_mode
    data["error"] = error
    data["login_label"] = _("Log In")
    data["contact_subject"] = quote(_("Trouble logging in"))

    response = render(request, 'accounts/login.haml', data)

    _append_login_mode_cookie(response, login_mode)

    # if loading the login page
    # then remove all LMS-bound wildcard cookies which may have been set in the past. We do that
    # by setting a cookie that already expired
    _expire_session_cookies(response)

    return response


def login_post_view(request):
    form = LoginIdForm(request.POST)
    # Check if we just want to validate the login id
    if form.is_valid():
        if 'validate_login_id' in request.POST:
            # Check if user has an SSO account set up
            try:
                provider = get_sso_provider(form.cleaned_data['login_id'])
                if provider:
                    # If SSO is set up redirect use to login via SSO
                    redirect_url = _build_sso_redirect_url(provider, reverse('login'))
                    response = HttpResponseRedirect(redirect_url)
                    _append_login_mode_cookie(response, 'sso')
                    return response

                # Otherwise check if the username / email is valid
                username = get_username_for_login_id(form.cleaned_data['login_id'])
                if username:
                    return JsonResponse({"login_id": "valid"})
            except ApiError as err:
                return JsonResponse({"error": err.message}, status=401)

            # Invalid or missing username/email
            return JsonResponse({
                "login_id": _("Username/email is not recognised. Try again.")
            }, status=403)

        # normal login
        try:
            login_id = form.cleaned_data['login_id']
            password = form.cleaned_data['password']
            username = get_username_for_login_id(login_id)
            user = auth.authenticate(username=username, password=password)
            if user:
                response = _process_authenticated_user(request, user)
                _append_login_mode_cookie(response, login_mode='normal')
                append_user_mobile_app_id_cookie(response, user.id)
                return response
            else:
                return JsonResponse({
                    "password": _("Password doesn't match our records. Try again.")
                }, status=403)

        except ApiError as err:
            return JsonResponse({"error": err.message}, status=500)

    # If form validation fails it's due to a longer than 255-char username
    return JsonResponse({
        "login_id": _("Username/email is not recognised. Try again.")
    }, status=403)


@require_http_methods(['GET'])
def sso_launch(request):
    ''' Initiates the SSO process for mobile clients. '''
    provider = None
    provider_id = request.GET.get('provider_id', None)
    mobile_url_scheme = request.GET.get('mobile_url_scheme', None)

    if provider_id is not None:
        provider = "-".join(provider_id.split("-")[1:])

    # If provider is not provided or is in an invalid format that doesn't include a ``-``
    if not provider:
        error = {"error": "invalid_provider_id"}
        if mobile_url_scheme is not None:
            return _build_mobile_redirect_response(request, error)
        return JsonResponse(error, status=400)

    redirect_url = _build_sso_redirect_url(provider, reverse('sso_finalize'))
    response = HttpResponseRedirect(redirect_url)

    _append_login_mode_cookie(response, 'sso')
    if mobile_url_scheme is not None:
        _append_mobile_url_scheme_cookie(response, mobile_url_scheme)

    return response


def get_username_for_login_id(login_id):
    if '@' in login_id:
        user = user_api.get_users(email=login_id)
    else:
        user = user_api.get_users(username=login_id)
    if user:
        return user[0].username


def finalize_sso_mobile(request):
    '''
    Handles getting Oauth2 credentials for mobile and redirecting to native app
    url.
    '''
    error = request.GET.get('error', None)

    if error is not None:
        return _build_mobile_redirect_response(request, {'error': error})

    # If we already have a code, it's because we've already completed the
    # OAuth2 authorization process
    code = request.GET.get('code', None)
    if code is not None:
        # Get an access token that the mobile app can use
        try:
            response = requests.post(
                request.build_absolute_uri("{access_token_path}".format(
                    access_token_path=OAUTH2_ACCESS_TOKEN_PATH,
                )),
                data={
                    'client_id': settings.OAUTH2_MOBILE_CLIENT_ID,
                    'client_secret': settings.OAUTH2_MOBILE_CLIENT_SECRET,
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': request.build_absolute_uri(reverse('sso_finalize')),
                },
            )
            if response.status_code // 100 == 5:
                response.raise_for_status()
            oauth_data = response.json()
            return _build_mobile_redirect_response(request, oauth_data)
        except ConnectionError:
            # Unable to connect to server
            return _build_mobile_redirect_response(request, {'error': 'connection_error'})
        except (HTTPError, ValueError):
            # Server raised a 500 status, or returned a response that couldn't be parsed as JSON
            return _build_mobile_redirect_response(request, {'error': 'server_error'})

    # We don't have an authorization code yet, so redirect users to the authorization url.
    # NOTE: This shouldn't need input from the user if the client is marked as trusted.
    oauth_data = {
        'client_id': settings.OAUTH2_MOBILE_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': request.build_absolute_uri(reverse('sso_finalize')),
    }
    access_token_redirect = "{authorize_path}?{query}".format(
        authorize_path=OAUTH2_AUTHORIZE_PATH,
        query=urlencode(oauth_data)
    )
    return HttpResponseRedirect(access_token_redirect)


def logout(request):
    response = logout_handler.logout(request)
    _expire_session_cookies(response)
    return response


def activate(request, activation_code, registration=None):
    ''' handles requests for activation form and their submission '''
    error = None
    user = None
    user_data = None
    initial_data = {}
    try:
        activation_record = UserActivation.objects.get(activation_key=activation_code)
        user = user_api.get_user(activation_record.user_id)

        if user.is_active:
            raise

        #get registration object to prepopulate/hide fields in form if user came from registration form
        if registration:
            try:
                registration_request = PublicRegistrationRequest.objects.get(company_email=user.email)
            except:
                registration_request = None

        for field_name in VALID_USER_FIELDS:
            if field_name == "full_name":
                initial_data[field_name] = user.formatted_name
            elif hasattr(user, field_name):
                initial_data[field_name] = getattr(user, field_name)

        # See if we have a company for this user
        companies = user_api.get_user_organizations(user.id)
        if len(companies) > 0:
            company = companies[0]
            initial_data["company"] = company.display_name

    except:
        return HttpResponseRedirect('/accounts/login/?account_activate_check=True')

    if request.method == 'POST' and error is None:  # If the form has been submitted...
        user_data = request.POST.copy()

        # email should never be changed
        user_data["email"] = user.email
        form = ActivationForm(
            user_data, initial=initial_data
        )
        if form.is_valid():  # All validation rules pass
            try:
                login_mode = 'normal'

                user_activation_with_data(user.id, form.cleaned_data, activation_record)

                user = auth.authenticate(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password']
                )
                if user:
                    response = _process_authenticated_user(request, user, activate_account=True)
                    _append_login_mode_cookie(response, login_mode)
                    append_user_mobile_app_id_cookie(response, user.id)
                    return response

            except ActivationError as activation_error:
                error = activation_error.value
                form.fields["company"].widget = HiddenInput()
                form.fields["title"].widget = HiddenInput()
        elif not error:
            if registration:
                form.fields["company"].widget = HiddenInput()
                form.fields["title"].widget = HiddenInput()
            error = _("Some required information was missing. Please check the fields below.")
    else:
        form = ActivationForm(user_data, initial=initial_data)

        # set focus to username field
        form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})

        if registration:
            form.fields["company"].widget = HiddenInput()
            form.fields["title"].widget = HiddenInput()
            if registration_request:
                form.fields["title"].widget.attrs.update({'readonly': 'readonly'})
                initial_data["full_name"] = registration_request.first_name + " " + registration_request.last_name
                initial_data["title"] = registration_request.current_role

    data = {
        "user": user,
        "form": form,
        "error": error,
        "activation_code": activation_code,
        "activate_label": _("Create my McKinsey Academy account"),
        }
    return render(request, 'accounts/activate.haml', data)

def activate_v2(request, activation_code):
    ''' handles requests for activation form and their submission '''
    error = None
    user = None
    user_data = None
    initial_data = {}
    try:
        activation_record = UserActivation.objects.get(activation_key=activation_code)
        user = user_api.get_user(activation_record.user_id)
        if user.is_active:
            raise

        for field_name in VALID_USER_FIELDS:
            if field_name == "full_name":
                initial_data[field_name] = user.formatted_name
            elif hasattr(user, field_name):
                initial_data[field_name] = getattr(user, field_name)

        # See if we have a company for this user
        companies = user_api.get_user_organizations(user.id)
        if len(companies) > 0:
            company = companies[0]
            initial_data["company"] = company.display_name

    except:
        user_data = None
        error = _("Invalid Activation Code")

    if request.method == 'POST' and error is None:  # If the form has been submitted...
        user_data = request.POST.copy()

        # email should never be changed
        user_data["email"] = user.email

        form = ActivationFormV2(user_data)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                user_activation_with_data(user.id, user_data, activation_record)

                # Redirect after POST
                return HttpResponseRedirect(
                    '/accounts/login?username={}'.format(
                        user_data["username"]
                    )
                )
            except ActivationError as activation_error:
                error = activation_error.value
        elif not error:
            error = _("Some required information was missing. Please check the fields below.")
    else:
        form = ActivationFormV2(user_data, initial=initial_data)

        # set focus to username field
        form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "user": user,
        "form": form,
        "error": error,
        "activation_code": activation_code,
        "activate_label": _("Create my McKinsey Academy account"),
        }
    return render(request, 'accounts/activate.haml', data)

@csrf_exempt
def sso_finalize(request):
    '''
    Call the desktop SSO registration view, or the mobile view. If already
    logged in redirect to the home page.
    '''

    # If a mobile_url_scheme is defined, this view is called as part of the
    # mobile SSO auth flow.
    scheme = _get_mobile_url_scheme(request)
    if scheme is not None:
        return finalize_sso_mobile(request)

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('protected_home'))

    return finalize_sso_registration(request)


@require_POST
def finalize_sso_registration(request):
    ''' Validate SSO data sent by the LMS, then display the registration form '''
    # Check the data sent by the provider:
    hmac_key = settings.EDX_SSO_DATA_HMAC_KEY
    if isinstance(hmac_key, unicode):
        hmac_key = hmac_key.encode('utf-8')
    try:
        # provider_data will be a dict with keys of 'email', 'full_name', etc. from the provider.
        provider_data_str = base64.b64decode(request.POST['sso_data'])
        provider_data = json.loads(provider_data_str)
        hmac_digest = base64.b64decode(request.POST['sso_data_hmac'])
        expected_digest = hmac.new(hmac_key, msg=provider_data_str, digestmod=hashlib.sha256).digest()
    except Exception:
        log.exception("Error parsing/validating provider data (query parameter).")
        return HttpResponseBadRequest(_("No provider data found."))
    if hmac_digest != expected_digest:  # If we upgrade to Python 2.7.7+ use hmac.compare_digest instead
        return HttpResponseForbidden(_("Provider data does not seem valid."))

    # Store the provider data in the session and proceed to the registration form:
    request.session['provider_data'] = provider_data

    if SSO_ACCESS_KEY_SESSION_ENTRY not in request.session:
        request.session['sso_error_details'] = MISSING_ACCESS_KEY_ERROR
        return HttpResponseRedirect(reverse('sso_error'))

    return HttpResponseRedirect(reverse('sso_registration_form'))


def _cleanup_username(username):
    """
    Cleans up the username value that came from the SSO provider to pass validation checks.
    This is only used for the "suggested" username, and not used for any custom username entered
    by users into the form - that gets validated later when we call user_api.register_user(...).
    """
    username = username.replace(" ", "_")  # Replace spaces with underscores.
    # uses the same check as edx-platform/lms/djangoapps/api_manager/users/views.py:UsersDetail.post
    try:
        validate_slug(username)
    except ValidationError:
        initial, username = username, USERNAME_INVALID_CHARS_REGEX.sub("", username)
        log.info("Username '{initial_username}' does not pass validation checks; changed to '{actual_username}'".format(
            initial_username=initial, actual_username=username
        ))

    # Does the username already exist?
    try:
        if username and user_api.get_users(username=username):
            # Try appending increasing numbers to the username to create a unique username.
            username_base, append_number = username.rstrip(string.digits), 1
            while True:
                username = "{}{}".format(username_base, append_number)
                if not user_api.get_users(username=username):
                    break  # We found an unused username
                if append_number > 1000:
                    break  # Give up trying to find a number high enough.
                append_number += 1 if append_number < 10 else random.randrange(1,100)
    except ApiError:
        log.exception("Error when checking username uniqueness.")
        pass
    return username


def sso_registration_form(request):
    ''' handles requests for activation form and their submission '''
    if request.user.is_authenticated():
        # The user should not be logged in or even registered at this point.
        return HttpResponseRedirect(reverse('protected_home'))

    # The user must have come from /access/ with a valid AccessKey:
    if SSO_ACCESS_KEY_SESSION_ENTRY not in request.session:
        return HttpResponseForbidden(_('Access Key missing.'))
    try:
        access_key, client = _get_access_key(request.session[SSO_ACCESS_KEY_SESSION_ENTRY])
    except (AccessKey.DoesNotExist, AttributeError, IndexError):
        return HttpResponseNotFound()

    error = None
    provider_data = request.session['provider_data']
    provider_user_data = provider_data['user_details']
    username = _cleanup_username(provider_user_data.get('username', ''))
    remote_session_key = request.COOKIES.get('sessionid')

    if remote_session_key:
        user_data = {
            'accept_terms': True,
            'city': settings.SSO_AUTOPROVISION_CITY,
            'username': username,
        }

        initial_values = {  # Default values from the provider:
            'username': username,
        }
        fixed_values = {  # Values that we prevent the user from editing:
            'company': client.display_name,
        }
        # We also set a fixed value for full name and email, but only if we got those from the provider:
        if provider_user_data.get('fullname'):
            fixed_values['full_name'] = provider_user_data['fullname']  # provider uses 'fullname', we use 'full_name'
        if provider_user_data.get('email'):
            fixed_values['email'] = provider_user_data['email']

        form = FinalizeRegistrationForm(user_data, fixed_values, initial=initial_values)
        if form.is_valid():
            # Create a random secure password for this user:
            random_password = base64.b64encode(os.urandom(32))
            registration_data = form.cleaned_data.copy()
            registration_data['password'] = random_password
            registration_data['is_active'] = True
            # Create an account for this user and log them in:
            try:
                user_api.register_user(registration_data)
                new_user = auth.authenticate(
                    username=registration_data['username'],
                    password=random_password,
                    remote_session_key=remote_session_key
                )
                auth.login(request, new_user)

                _process_access_key_and_remove_from_session(request, new_user, access_key, client)

                # Redirect to the LMS to link the user's account to the provider permanently:
                complete_url = '{lms_auth}complete/{backend_name}/'.format(
                    lms_auth=settings.LMS_AUTH_URL,
                    backend_name=provider_data['backend_name'],
                )
                return HttpResponseRedirect(complete_url)
            except ApiError as exc:
                error = _("Failed to register user: {exception_message}").format(exception_message=exc.message)
        else:
            error = _("Some required information was missing.")
    else:
        error = _("Authentication cookie is missing. Your session may have timed out. Please start over.")

    context = {'error_details': error}
    return render(request, 'accounts/sso_error.haml', context)


def sso_error(request):
    ''' The LMS will redirect users here if an SSO error occurs '''
    # If a mobile_url_scheme is defined, this view is called as part of the
    # mobile SSO auth flow.
    scheme = _get_mobile_url_scheme(request)
    error_details = request.session.get('sso_error_details')
    error = request.session.get('error')

    if scheme is not None:
        return _build_mobile_redirect_response(request, {
            'error': error or error_details or 'Unknown SSO Error'
        })

    context = {'error_details': error_details}
    return render(request, 'accounts/sso_error.haml', context)

@ajaxify_http_redirects
def reset_confirm(request, uidb64=None, token=None,
                  template_name='registration/password_reset_confirm.html',
                  post_reset_redirect='/accounts/login?reset=complete',
                  set_password_form=SetNewPasswordForm,
                  current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert uidb64 is not None and token is not None # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = user_api.get_user(uid)
    except (TypeError, ValueError, OverflowError):
        user = None

    reset_record = None
    if user is not None:
        reset_record = UserPasswordReset.check_user_validation_record(user, token, datetime.datetime.now())

    if reset_record is not None:
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                user = form.save()
                if hasattr(user, 'error'):
                    from django.forms.utils import ErrorList
                    errors = form._errors.setdefault("new_password1", ErrorList())
                    errors.append(user.error)
                else:
                    reset_record.delete()
                    return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

@ajaxify_http_redirects
def reset(request, is_admin_site=False,
          template_name='registration/password_reset_form.haml',
          password_reset_form=FpasswordForm,
          email_template_name='registration/password_reset_email.haml',
          subject_template_name='registration/password_reset_subject.haml',
          post_reset_redirect='/accounts/login?reset=done',
          from_email=settings.APROS_EMAIL_SENDER,
          current_app=None,
          extra_context=None):

    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            '''
            Doing user check here and in save function, because it should be part of save function
            (if called elsewhere) but here I need it to check post_reset_redirect link
            '''
            email = form.cleaned_data["email"]
            users = user_api.get_users(email=email)
            if len(users) < 1:
                post_reset_redirect = '/accounts/login?reset=failed'
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

@ajaxify_http_redirects
def reset_done(request,
               template_name='registration/password_reset_done.haml',
               current_app=None, extra_context=None):
    return password_reset_done(request=request,
               template_name=template_name,
               current_app=current_app, extra_context=extra_context)


@ajaxify_http_redirects
def reset_complete(request,
                   template_name='registration/password_reset_complete.haml',
                   current_app=None, extra_context=None):
    return password_reset_complete(request=request,
                   template_name=template_name,
                   current_app=current_app, extra_context=extra_context)


def home(request):
    ''' show me the home page '''

    programData = standard_data(request)
    program = programData.get('program')
    course = programData.get('course')

    data = {'popup': {'title': '', 'description': ''}}
    if request.session.get('program_popup') is None:
        if program:
            if program.id is not Program.NO_PROGRAM_ID:
                days = ''
                if course and course.start is not None and course.start > datetime.datetime.today():
                    days = str(
                        int(math.floor(((course.start - datetime.datetime.today()).total_seconds()) / 3600 / 24))) + ' day'
                elif hasattr(program, 'start_date') and program.start_date > datetime.datetime.today():
                    days = str(
                        int(math.floor(((program.start_date - datetime.datetime.today()).total_seconds()) / 3600 / 24))) + ' day'
                if days is not '':
                    if days > 1:
                        days = days + 's'
                    popup = {'title': '', 'description': ''}
                    popup['title'] = _("Welcome to McKinsey Academy")
                    popup['description'] = _("Your program will start in {days} days. "
                                             "Please explore the site to learn more about the "
                                             "experience in the meantime.").format(days=days)
                    if course:
                        popup['description'] = _("Your course begins in {days} days. "
                                                 "Before the course begins, "
                                                 "you can explore this site to learn more about "
                                                 "what to expect.").format(days=days)
                        data.update({'course': course})
                    data.update({'program': program, 'popup': popup})
                    request.session['program_popup'] = True
    cells = []
    with open('main/fixtures/landing_data.json') as json_file:
        landing_tiles = json.load(json_file)
        for tile in landing_tiles["order"]:
            tileset = landing_tiles[tile]
            cells.append(tileset.pop(random.randrange(len(tileset))))

    # if mobile device then display login button on the basis of
    # `LOGIN_BUTTON_FOR_MOBILE_ENABLED` setting
    data.update({'is_login_button_enabled': True})
    if is_mobile_user_agent(request):
        data.update(
            {'is_login_button_enabled': settings.LOGIN_BUTTON_FOR_MOBILE_ENABLED}
        )
    data.update({"user": request.user, "cells": cells})

    if 'username' in request.GET:
        mobile_popup_data = get_mobile_app_download_popup_data(request)
        data.update(mobile_popup_data)

    return render(request, 'home/landing.haml', data)


@login_required
def protected_home(request):
    return home(request)


@login_required
@never_cache
def user_profile(request):
    ''' gets user_profile information in html snippet '''
    user = user_api.get_user(request.user.id)
    user_data = {
        "user_image_url": user.image_url_large,
        "user": user
    }

    user_data = add_edx_notification_context(user_data)

    # using render_to_string to avoid Context evaluation
    content = render_to_string('accounts/user_profile.haml', user_data, request=request)

    return HttpResponse(content)


@login_required
def user_profile_image_edit(request):
    if request.method == 'POST':
        user_id = request.user.id
        left = int(float(request.POST.get('x1-position')))
        top = int(float(request.POST.get('y1-position')))
        right = int(float(request.POST.get('width-position'))) + left
        bottom = int(float(request.POST.get('height-position'))) + top
        temp_image = request.FILES['profile_image']

        from PIL import Image
        original = Image.open(temp_image)
        cropped_example = original.crop((left, top, right, bottom))
        avatar_image_io = StringIO.StringIO()
        cropped_example.convert('RGB').save(avatar_image_io, format='JPEG')
        avatar_image_io.seek(0)
        avatar_file_data = {'file': ('avatar.jpg', avatar_image_io, 'image/jpeg')}
        response = platform_api.update_user_profile_image(
            request.user,
            avatar_file_data
        )

        RemoteUser.remove_from_cache(user_id)

        return change_profile_image(request, user_id, template='edit_profile_image')


@login_required
def change_profile_image(request, user_id, template='change_profile_image', user_profile_image=None, error=None):
    ''' handles requests for login form and their submission '''

    if user_profile_image:
        profile_image = user_profile_image
    else:
        user = user_api.get_user(user_id)
        profile_image = user.image_url_full

    if '?' in profile_image:
        profile_image = profile_image + '&' + format(datetime.datetime.now(), u'U')
    else:
        profile_image = profile_image + '?' + format(datetime.datetime.now(), u'U')
    form = UploadProfileImageForm(request)  # An unbound form

    data = {
        "form": form,
        "user_id": user_id,
        "error": error,
        "profile_image": profile_image,
    }

    return render(
        request,
        'accounts/{}.haml'.format(template),
        data
    )


def load_profile_image(request, image_url):
    from django.core.files.storage import default_storage
    image_url = 'images/' + image_url
    if default_storage.exists(image_url):
        image = default_storage.open(image_url).read()
        from mimetypes import MimeTypes
        import urllib
        mime = MimeTypes()
        url = urllib.pathname2url(image_url)
        mime_type = mime.guess_type(url)
        return HttpResponse(
                image, content_type=mime_type[0]
            )

@login_required
def edit_fullname(request):
    ''' edit full name form '''
    error = None
    if request.method == 'POST':
        form = EditFullNameForm(request.POST)
        if form.is_valid():
            try:
                user_api.update_user_information(request.user.id, {
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name']
                })
            except ApiError as err:
                error = err.message
    else:
        form = EditFullNameForm()

    user_data = {
        'error': error,
        'title':  _('Enter your full name'),
        'form': form,
        'submit_label': _('Save')
    }
    return render(request, 'accounts/edit_field.haml', user_data)

@login_required
def edit_title(request):
    ''' edit title form '''
    error = None
    if request.method == 'POST':
        form = EditTitleForm(request.POST)
        if form.is_valid():
            try:
                user_api.update_user_information(request.user.id, {
                    'title': form.cleaned_data['title']
                })
            except ApiError as err:
                error = err.message
    else:
        form = EditTitleForm()
    user_data = {
        'error': error,
        'title': _('Enter your title'),
        'form': form,
        'submit_label': _('Save')
    }
    return render(request, 'accounts/edit_field.haml', user_data)


def access_key(request, code):
    template = 'accounts/access.html'
    # Try to find the unique code.
    try:
        key, client = _get_access_key(code)
    except (AccessKey.DoesNotExist, AttributeError, IndexError):
        log.exception("Invalid AccessKey. The key or associated client could not be loaded.")
        return render(request, template, status=404)

    # If already authenticated, add to a program and enroll to a course, than redirect back to home page
    if request.user.is_authenticated():
        if key and client:
            _process_access_key_and_remove_from_session(request, request.user, key, client)
        return HttpResponseRedirect(_get_redirect_to_current_course(request))

    # Show the invitation landing page. It informs the user that they are about
    #  to be redirected to their company's provider.

    try:
        customization = ClientCustomization.objects.get(client_id=key.client_id)
    except ClientCustomization.DoesNotExist as err:
        return render(request, template, status=404)

    if not customization.identity_provider:
        return render(request, template, status=404)

    request.session[SSO_ACCESS_KEY_SESSION_ENTRY] = key.code
    # all SSO requests that might end up with user logged in must go through login view to allow session detection
    # The rule of thumb: it should be either the `login` itself, or a view with `login_required` decorator
    redirect_to = _build_sso_redirect_url(customization.identity_provider, reverse('login'))

    data = {
        'redirect_to': redirect_to
    }

    return render(request, template, data)


def demo_registration(request, course_run_name):

    try:
        course_run = CourseRun.objects.get(name=course_run_name)
    except ObjectDoesNotExist:
        course_run = None

    registration_status = _("Initial")

    if course_run:
        if request.method == 'POST':
            form = PublicRegistrationForm(request.POST, course_run_name=course_run_name)
            if form.is_valid():
                registration_request = form.save(commit=False)
                registration_request.course_run = course_run

                if OTHER_ROLE == registration_request.current_role:
                    registration_request.current_role = registration_request.current_role_other
                    registration_request.current_role_other == None

                registration_request.mcka_user = True if settings.MCKINSEY_EMAIL_DOMAIN in registration_request.company_email else False

                #todo check for better api approach
                users = user_api.get_users(email=registration_request.company_email)
                registration_request.new_user = True if len(users) < 1 else False

                _set_number_of_enrolled_users(course_run)
                registration_request.save()

                if course_run.total_participants == settings.COURSE_RUN_PARTICIPANTS_TRESHOLD:
                    send_warning_email_to_admin(course_run)

                if (course_run.total_participants >= course_run.max_participants) or not course_run.is_open:
                    _process_course_run_closed(registration_request, course_run)
                    registration_status = _("Course Closed")

                #if existing user, send user object
                if registration_status == _("Initial"):
                    try:
                        if not registration_request.new_user:
                            process_registration_request(request, registration_request, course_run, users[0])
                        else:
                            process_registration_request(request, registration_request, course_run)
                        registration_status = _("Registered")
                    except ValueError:
                        registration_status = _("Error")
        else:
            form = PublicRegistrationForm(course_run_name=course_run_name)

        data = {
            'form': form,
            'course_run_name': course_run_name,
            'course_run': course_run,
            'registration_status': registration_status,
            'home_url': reverse('home'),
            'program': True # header css issue
        }

        return render(request, 'accounts/public_registration.haml', data)

    else:
        return render(request, '404.haml')

def switch_language_based_on_preference(request):
    try:
        language_code = request.GET.get('LANG')
    except AttributeError:
        language_code = request.LANGUAGE_CODE
    set_language(language_code)
    referer = get_referer_from_request(request)
    response = HttpResponseRedirect(referer)
    if [lang for lang in LANGUAGES if lang[0] == language_code]:
        response.set_cookie(
            'preferred_language',
            language_code,
            expires=COOKIES_YEARLY_EXPIRY_TIME
        )
    return response
