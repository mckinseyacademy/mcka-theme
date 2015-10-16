''' views for auth, sessions, users '''
import base64
import hashlib
import hmac
import json
import os
import random
import urlparse
from urllib import urlencode
import datetime
import math
import logging
import string
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib import auth, messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from api_client import user_api
from api_client.json_object import JsonObjectWithImage
from api_client.api_error import ApiError
from admin.models import Client, Program
from admin.controller import load_course
from admin.models import AccessKey, ClientCustomization
from courses.user_courses import standard_data, get_current_course_for_user, get_current_program_for_user

from .models import RemoteUser, UserActivation, UserPasswordReset
from .controller import (
    user_activation_with_data, ActivationError, is_future_start, get_sso_provider,
    process_access_key
)
from .forms import (
    LoginForm, ActivationForm, FinalizeRegistrationForm, FpasswordForm, SetNewPasswordForm, UploadProfileImageForm, 
    EditFullNameForm, EditTitleForm, SSOLoginForm
)
from django.shortcuts import resolve_url
from django.utils.http import urlsafe_base64_decode
from django.utils.dateformat import format
from django.template.response import TemplateResponse

import logout as logout_handler

from django.contrib.auth.views import password_reset_done, password_reset_complete
from django.core.urlresolvers import reverse, resolve, Resolver404
from admin.views import ajaxify_http_redirects

log = logging.getLogger(__name__)

VALID_USER_FIELDS = ["email", "first_name", "last_name", "full_name", "city", "country", "username", "level_of_education", "password", "is_active", "year_of_birth", "gender", "title", "avatar_url"]
USERNAME_INVALID_CHARS_REGEX = re.compile("[^-\w]")

LOGIN_MODE_COOKIE = 'login_mode'
SSO_ACCESS_KEY_SESSION_ENTRY = 'sso_access_key_id'
SSO_AUTH_ENTRY = 'apros'

MISSING_ACCESS_KEY_ERROR = _("Your login did not match any known accounts, a registration key is required "
                             "in order to create a new account.")
CANT_PROCESS_ACCESS_KEY = _("There was an error enrolling you in a course using the registration key you provided")

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


def _process_authenticated_user(request, user):
    redirect_to = _get_redirect_to(request)
    _validate_path(redirect_to)

    request.session["remote_session_key"] = user.session_key
    auth.login(request, user)

    if not redirect_to:
        course_id = get_current_course_for_user(request)
        program = get_current_program_for_user(request)
        future_start_date = False
        if program:
            if course_id is not None:
                for program_course in program.courses:
                    if program_course.id == course_id:
                        '''
                        THERE IS A PLACE FOR IMPROVEMENT HERE
                        IF user course object had start/due date, we
                        would do one less API call
                        '''
                        full_course_object = load_course(course_id)
                        if hasattr(full_course_object, 'start'):
                            future_start_date = is_future_start(full_course_object.start)
                        elif hasattr(program, 'start_date') and future_start_date is False:
                            future_start_date = is_future_start(program.start_date)
            elif hasattr(program, 'start_date') and future_start_date is False:
                future_start_date = is_future_start(program.start_date)

        if course_id:
            if future_start_date:
                redirect_to = '/'
            else:
                redirect_to = '/courses/{}'.format(course_id)
        else:
            redirect_to = '/'

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
            domain=settings.LMS_SESSION_COOKIE_DOMAIN,
        )

    if SSO_ACCESS_KEY_SESSION_ENTRY in request.session:
        try:
            access_key, client = _get_access_key(request.session[SSO_ACCESS_KEY_SESSION_ENTRY])
        except (AccessKey.DoesNotExist, AttributeError, IndexError):
            messages.error(request, CANT_PROCESS_ACCESS_KEY)
            return response

        _process_access_key_and_remove_from_session(request, user, access_key, client)

    return response


def _process_access_key_and_remove_from_session(request, user, access_key, client):
    if SSO_ACCESS_KEY_SESSION_ENTRY in request.session:
        del request.session[SSO_ACCESS_KEY_SESSION_ENTRY]
    processing_messages = process_access_key(user, access_key, client)
    for message_level, message in processing_messages:
        messages.add_message(request, message_level, message)


def _get_access_key(key_code):
    access_key = AccessKey.objects.get(code=key_code)
    client = Client.fetch(access_key.client_id)
    return access_key, client


def _append_login_mode_cookie(response, login_mode):
    response.set_cookie(
        LOGIN_MODE_COOKIE, login_mode, expires=datetime.datetime.utcnow() + datetime.timedelta(days=365)
    )


def _expire_session_cookies(response):
    expire_in_past = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    response.set_cookie('sessionid', 'to-delete', domain=settings.LMS_SESSION_COOKIE_DOMAIN, expires=expire_in_past)
    response.set_cookie('csrftoken', 'to-delete', domain=settings.LMS_SESSION_COOKIE_DOMAIN, expires=expire_in_past)


def login(request):
    ''' handles requests for login form and their submission '''
    error = None
    request.session['ddt'] = False  # Django Debug Tool session key init.

    # Redirect IE to home page, login not available
    if request.META.has_key('HTTP_USER_AGENT'):
        ua = request.META['HTTP_USER_AGENT'].lower()
        if re.search('msie [1-8]\.', ua):
            return HttpResponseRedirect('/')

    form = None
    sso_login_form = None
    login_mode = request.COOKIES.get(LOGIN_MODE_COOKIE, 'normal')
    expire_in_past = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    if request.method == 'POST':  # If the form has been submitted...
        if 'sso_login_form_marker' not in request.POST:
            # normal login
            login_mode = 'normal'
            form = LoginForm(request.POST)
            if form.is_valid():
                try:
                    user = auth.authenticate(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password']
                    )
                    if user:
                        response = _process_authenticated_user(request, user)
                        _append_login_mode_cookie(response, login_mode)
                        return response

                except ApiError as err:
                    error = err.message
        else:
            # SSO login
            sso_login_form = SSOLoginForm(request.POST)
            login_mode = 'sso'
            if sso_login_form.is_valid():
                provider = get_sso_provider(sso_login_form.cleaned_data['email'])
                if provider:
                    redirect_url = _build_sso_redirect_url(provider, reverse('login'))
                    response = HttpResponseRedirect(redirect_url)
                    _append_login_mode_cookie(response, login_mode)
                    return response
                else:
                    error = _(u"This email is not associated with any identity provider")

    elif request.method == 'GET' and 'sessionid' in request.COOKIES:
        # The user may already be logged in to the LMS.
        # (e.g. they used the LMS's third_party_auth to authenticate, then got redirected back here)
        try:
            user = auth.authenticate(remote_session_key=request.COOKIES['sessionid'])
            if user:
                response = _process_authenticated_user(request, user)
                _append_login_mode_cookie(response, login_mode)
                return response
        except ApiError as err:
            error = err.message

    elif 'username' in request.GET:
        # password fields get cleaned upon rendering the form, but we must
        # provide something here, otherwise the error (password field is
        # required) will appear
        form = LoginForm(
            {"username": request.GET['username'], "password": "fake_password"}
        )
        # set focus to password field
        form.fields["password"].widget.attrs.update({'autofocus': 'autofocus'})
    elif 'reset' in request.GET:
        form = LoginForm()
        # set focus to username field
        form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})
        form.reset = request.GET['reset']
    else:
        form = LoginForm()
        # set focus to username field
        form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "user": None,
        "form": form or LoginForm(),
        "sso_login_form": sso_login_form or SSOLoginForm(),
        "login_mode": login_mode,
        "error": error,
        "login_label": _("Log in to my McKinsey Academy account & access my courses"),
    }
    response = render(request, 'accounts/login.haml', data)

    _append_login_mode_cookie(response, login_mode)

    if request.method == 'GET':
        # if loading the login page
        # then remove all LMS-bound wildcard cookies which may have been set in the past. We do that
        # by setting a cookie that already expired
        _expire_session_cookies(response)

    return response


def logout(request):
    response = logout_handler.logout(request)
    _expire_session_cookies(response)
    return response


def activate(request, activation_code):
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

        form = ActivationForm(user_data)  # A form bound to the POST data
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
        form = ActivationForm(user_data, initial=initial_data)

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
@require_POST
def finalize_sso_registration(request):
    ''' Validate SSO data sent by the LMS, then display the registration form '''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('protected_home'))

    # Check the data sent by the provider:
    hmac_key = settings.EDX_SSO_DATA_HMAC_KEY
    if isinstance(hmac_key, unicode):
        hmac_key = hmac_key.encode('utf-8')
    try:
        # provider_data will be a dict with keys of 'email', 'full_name', etc. from the provider.
        provider_data_str = base64.b64decode(request.POST['sso_data'])
        provider_data = json.loads(provider_data_str)['user_details']
        hmac_digest = base64.b64decode(request.POST['sso_data_hmac'])
        expected_digest = hmac.new(hmac_key, msg=provider_data_str, digestmod=hashlib.sha256).digest()
    except Exception:
        log.exception("Error parsing/validating provider data (query parameter).")
        return HttpResponseBadRequest("No provider data found.")
    if hmac_digest != expected_digest:  # If we upgrade to Python 2.7.7+ use hmac.compare_digest instead
        return HttpResponseForbidden("Provider data does not seem valid.")

    # Store the provider data in the session and proceed to the registration form:
    request.session['provider_data'] = provider_data

    if SSO_ACCESS_KEY_SESSION_ENTRY not in request.session:
        request.session['sso_error_details'] = MISSING_ACCESS_KEY_ERROR
        return HttpResponseRedirect(reverse('sso_error'))

    return HttpResponseRedirect(reverse('sso_registration_form'))


def _cleanup_username(username):
    """ Cleans up username to pass validation checks """
    # uses the same check as edx-platform/lms/djangoapps/api_manager/users/views.py:UsersDetail.post
    try:
        validate_slug(username)
    except ValidationError:
        initial, username = username, USERNAME_INVALID_CHARS_REGEX.sub("", username)
        log.info("Username '{initial_username}' does not pass validation checks; changed to '{actual_username}'".format(
            initial_username=initial, actual_username=username
        ))
    return username


def sso_registration_form(request):
    ''' handles requests for activation form and their submission '''
    if request.user.is_authenticated():
        # The user should not be logged in or even registered at this point.
        return HttpResponseRedirect(reverse('protected_home'))

    # The user must have come from /access/ with a valid AccessKey:
    if SSO_ACCESS_KEY_SESSION_ENTRY not in request.session:
        return HttpResponseForbidden('Access Key missing.')
    try:
        access_key, client = _get_access_key(request.session[SSO_ACCESS_KEY_SESSION_ENTRY])
    except (AccessKey.DoesNotExist, AttributeError, IndexError):
        return HttpResponseNotFound()

    error = None
    user_data = None
    provider_data = request.session['provider_data']

    remote_session_key = request.COOKIES.get('sessionid')
    if not remote_session_key:
        error = _("Authentication cookie is missing.")

    if request.method == 'POST':
        user_data = request.POST.copy()

    username = _cleanup_username(provider_data.get('username', ''))

    initial_values = {  # Default values from the provider that the user can change:
        'username': username,
    }
    fixed_values = {  # Values that we prevent the user from editing:
        'company': client.display_name,
    }
    # We also set a fixed value for full name and email, but only if we got those from the provider:
    if provider_data.get('fullname'):
        fixed_values['full_name'] = provider_data['fullname']  # provider uses 'fullname', we use 'full_name'
    if provider_data.get('email'):
        fixed_values['email'] = provider_data['email']

    form = FinalizeRegistrationForm(user_data, fixed_values, initial=initial_values)
    if request.method == 'POST' and error is None:
        if form.is_valid():  # If the form has been submitted...
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
                complete_url = '{lms_auth}complete/tpa-saml/'.format(lms_auth=settings.LMS_AUTH_URL)
                return HttpResponseRedirect(complete_url)
            except ApiError as exc:
                error = _("Failed to register user: {exception_message}".format(exception_message=exc.message))
        else:
            error = _("Some required information was missing. Please check the fields below.")

    data = {
        "form": form,
        "error": error,
        "activate_label": _("Create my McKinsey Academy account"),
    }
    return render(request, 'accounts/activate.haml', data)


def sso_error(request):
    ''' The LMS will redirect users here if an SSO error occurs '''
    context = {'error_details': request.session.get('sso_error_details')}
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
                    from django.forms.util import ErrorList
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
          subject_template_name='registration/password_reset_subject.txt',
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

    # Display any errors/messages that may have been created during SSO onboarding:
    flash_messages = messages.get_messages(request)
    if flash_messages:
        data['popup']['title'] = "Notice"
        data['popup']['description'] = " ".join(msg.message for msg in flash_messages)
    elif request.session.get('program_popup') is None:
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
                    popup['title'] = "Welcome to McKinsey Academy"
                    popup['description'] = "Your program will start in {}. Please explore the site to learn more about the experience in the meantime.".format(
                        days)
                    if course:
                        popup['description'] = "Your course begins in {}. Before the course begins, you can explore this site to learn more about what to expect.".format(
                            days)
                        data.update({'course': course})
                    data.update({'program': program, 'popup': popup})
                    request.session['program_popup'] = True
    cells = []
    with open('main/fixtures/landing_data.json') as json_file:
        landing_tiles = json.load(json_file)
        for tile in landing_tiles["order"]:
            tileset = landing_tiles[tile]
            cells.append(tileset.pop(random.randrange(len(tileset))))

    data.update({"user": request.user, "cells": cells})
    return render(request, 'home/landing.haml', data)

@login_required
def protected_home(request):
    return home(request)

@login_required
def user_profile(request):
    ''' gets user_profile information in html snippet '''
    user = user_api.get_user(request.user.id)
    user_data = {
        "user_image_url": user.image_url(size=160, path='absolute'),
        "user": user
    }

    return render(request, 'accounts/user_profile.haml', user_data)

@login_required
def user_profile_image_edit(request):
    if request.method == 'POST':
        user_id = request.user.id
        heightPosition = request.POST.get('height-position')
        widthPosition = request.POST.get('width-position')
        x1Position = request.POST.get('x1-position')
        x2Position = request.POST.get('x2-position')
        y1Position = request.POST.get('y1-position')
        y2Position = request.POST.get('y2-position')
        profileImageUrl = urlparse.urlparse(request.POST.get('upload-image-url'))[2]
        avatar_url = user_api.get_user(user_id).image_url(size=None, path='relative')

        from PIL import Image
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        image_url = _get_stored_image_url(request, profileImageUrl)
        if avatar_url != JsonObjectWithImage.default_image_url():
            avatar_url = _get_stored_image_url(request, avatar_url)

        if default_storage.exists(image_url):

            original = Image.open(default_storage.open(image_url))

            width, height = original.size   # Get dimensions
            left = int(x1Position)
            top = int(y1Position)
            right = int(x2Position)
            bottom = int(y2Position)
            cropped_example = original.crop((left, top, right, bottom))
            new_image_url = string.replace(image_url, settings.TEMP_IMAGE_FOLDER, '')
            JsonObjectWithImage.save_profile_image(cropped_example, avatar_url, new_image_url=new_image_url)
            user_api.update_user_information(user_id, {'avatar_url': '/accounts/' + new_image_url})
            request.user.avatar_url = '/accounts/' + new_image_url
            request.user.save()
        RemoteUser.remove_from_cache(user_id)

        # delete user profile images from TEMP_IMAGE_FOLDER
        temp_folder_path = 'images/' + settings.TEMP_IMAGE_FOLDER
        for filename in default_storage.listdir(temp_folder_path)[1]:
            if 'profile_image-{}'.format(user_id) in filename:
                default_storage.delete(temp_folder_path + filename)

        return change_profile_image(request, user_id, template='edit_profile_image')

@login_required
def change_profile_image(request, user_id, template='change_profile_image', user_profile_image=None, error=None):
    ''' handles requests for login form and their submission '''

    user = user_api.get_user(user_id)
    if user_profile_image:
        profile_image = user_profile_image
    else:
        profile_image = user.image_url(size=None, path='absolute')

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

@login_required
def upload_profile_image(request, user_id):
    ''' handles requests for login form and their submission '''
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        # A form bound to the POST data and FILE data
        form = UploadProfileImageForm(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass

            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            from PIL import Image

            temp_image = request.FILES['profile_image']
            allowed_types = ["image/jpeg", "image/png", 'image/gif', ]
            avatar_url = request.user.avatar_url

            if temp_image.content_type in allowed_types:
                temp_image_url = settings.TEMP_IMAGE_FOLDER + 'profile_image-{}-{}.jpg'.format(user_id, datetime.datetime.now().strftime("%s"))
                JsonObjectWithImage.save_profile_image(Image.open(temp_image), 'images/' + temp_image_url)
                avatar_url = '/accounts/images/' + temp_image_url
            else:
                error = "Error uploading file. Please try again and be sure to use an accepted file format."

            return HttpResponse(change_profile_image(request, request.user.id, template='change_profile_image', user_profile_image=avatar_url, error=error), content_type='text/html')
        else:
            error = "Error uploading file. Please try again and be sure to use an accepted file format."
            return HttpResponse(change_profile_image(request, request.user.id, template='change_profile_image', error=error), content_type='text/html')
    else:
        ''' adds a new image '''
        form = UploadProfileImageForm(request)  # An unbound form

    data = {
        "form": form,
        "user_id": user_id,
        "error": error,
    }

    return render(
        request,
        'accounts/upload_profile_image.haml',
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
                    'first_name': form.data['first_name'],
                    'last_name': form.data['last_name']
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
                    'title': form.data['title']
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

    key, client = None, None
    # Try to find the unique code.
    try:
        key, client = _get_access_key(code)
    except (AccessKey.DoesNotExist, AttributeError, IndexError):
        messages.error(request, CANT_PROCESS_ACCESS_KEY)

    # If already authenticated, add to a program and enroll to a course, than redirect back to home page
    if request.user.is_authenticated():
        if key and client:
            _process_access_key_and_remove_from_session(request, request.user, key, client)
        return HttpResponseRedirect(reverse('protected_home'))

    # Show the invitation landing page. It informs the user that they are about
    #  to be redirected to their company's provider.

    try:
        customization = ClientCustomization.objects.get(client_id=key.client_id)
    except ClientCustomization.DoesNotExist as err:
        return render(request, 'accounts/access.haml', status=404)

    if not customization.identity_provider:
        return render(request, 'accounts/access.haml', status=404)

    request.session[SSO_ACCESS_KEY_SESSION_ENTRY] = key.code
    # all SSO requests that might end up with user logged in must go through login view to allow session detection
    # The rule of thumb: it should be either the `login` itself, or a view with `login_required` decorator
    redirect_to = _build_sso_redirect_url(customization.identity_provider, reverse('login'))

    data = {
        'redirect_to': redirect_to
    }

    return render(request, 'accounts/access.haml', data)
