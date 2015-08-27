''' views for auth, sessions, users '''
import json
import random
import urlparse
import urllib2 as url_access
import datetime
import math
import logging
import string
import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import auth
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from api_client import user_api, course_api
from api_client.json_object import JsonObjectWithImage
from api_client.api_error import ApiError
from admin.models import Client, Program
from admin.controller import load_course
from courses.user_courses import standard_data, get_current_course_for_user, get_current_program_for_user

from django.core import mail
from django.test import TestCase
# from importlib import import_module
# SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
from .models import RemoteUser, UserActivation, UserPasswordReset
from .controller import user_activation_with_data, ActivationError, is_future_start
from .forms import LoginForm, ActivationForm, FpasswordForm, SetNewPasswordForm, UploadProfileImageForm, EditFullNameForm, EditTitleForm
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.dateformat import format
from django.template.response import TemplateResponse
from django.templatetags.static import static

import logout as logout_handler

from django.contrib.auth.views import password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.core.urlresolvers import reverse, resolve, Resolver404
from admin.views import ajaxify_http_redirects
from django.core.mail import send_mail

VALID_USER_FIELDS = ["email", "first_name", "last_name", "full_name", "city", "country", "username", "level_of_education", "password", "is_active", "year_of_birth", "gender", "title", "avatar_url"]

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

def login(request):
    ''' handles requests for login form and their submission '''
    error = None
    request.session['ddt'] = False  # Django Debug Tool session key init.

    # Redirect IE to home page, login not available
    if request.META.has_key('HTTP_USER_AGENT'):
        ua = request.META['HTTP_USER_AGENT'].lower()
        if re.search('msie [1-8]\.', ua):
            return HttpResponseRedirect('/')

    if request.method == 'GET' and 'sessionid' in request.COOKIES:
        # The user may already be logged in to the LMS.
        # (e.g. they used the LMS's third_party_auth to authenticate, then got redirected back here)
        try:
            user = auth.authenticate(remote_session_key=request.COOKIES['sessionid'])
        except ApiError as err:
            error = err.message
        if user:
            request.session["remote_session_key"] = user.session_key
            auth.login(request, user)

            redirect_to = None
            if 'HTTP_REFERER' in request.META:
                redirect_to = _get_qs_value_from_url('next', request.META['HTTP_REFERER'])

            if not redirect_to:
                redirect_to = request.GET.get('next', None)

            redirect_to = redirect_to or '/'
            return HttpResponseRedirect(redirect_to)

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

                _validate_path(redirect_to)

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

                hostname = request.get_host()
                wildcard_hostname = hostname
                try:
                    wildcard_hostname = '.'+string.join(hostname.split('.')[1:],'.')
                except:
                    pass

                # for localdev testing with a vagrant image
                # sometimes we want to set our cookies
                # as wildcards. If so, specify IS_EDXAPP_ON_SAME_DOMAIN=False
                # in the local_settings.py
                use_wildcards_for_cookies = not getattr(settings, 'IS_EDXAPP_ON_SAME_DOMAIN', True)

                if 'remote_session_key' in request.session:
                    response.set_cookie(
                        'sessionid',
                        request.session["remote_session_key"],
                        domain=wildcard_hostname if use_wildcards_for_cookies else None
                    )
                if hasattr(user, 'csrftoken'):
                    response.set_cookie(
                        'csrftoken',
                        user.csrftoken,
                        domain=wildcard_hostname if use_wildcards_for_cookies else None
                    )
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
        form = LoginForm()  # An unbound form
        # set focus to username field
        form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})
        form.reset = request.GET['reset']
    else:
        form = LoginForm()  # An unbound form
        # set focus to username field
        form.fields["username"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "user": None,
        "form": form,
        "error": error,
        "login_label": _("Log in to my McKinsey Academy account & access my courses"),
        }
    response = render(request, 'accounts/login.haml', data)

    if request.method == 'GET':
        # if loading the login page
        # then remove all LMS-bound wildcard cookies which may have been set in the past. We do that
        # by setting a cookie that already expired

        hostname = request.get_host()
        wildcard_hostname = hostname
        try:
            wildcard_hostname = '.'+string.join(hostname.split('.')[1:],'.')
        except:
            pass

        expire_in_past = datetime.datetime.strftime(datetime.datetime.utcnow() - datetime.timedelta(days=7), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie('sessionid', 'to-delete', domain=wildcard_hostname, expires=expire_in_past)
        response.set_cookie('csrftoken', 'to-delete', domain=wildcard_hostname, expires=expire_in_past)

    return response


def logout(request):
    return logout_handler.logout(request)

def activate(request, activation_code):
    ''' handles requests for activation form and their submission '''
    error = None
    user = None
    user_data = None
    try:
        activation_record = UserActivation.objects.get(activation_key=activation_code)
        user = user_api.get_user(activation_record.user_id)
        if user.is_active:
            raise

        user_data = {}
        for field_name in VALID_USER_FIELDS:
            if field_name == "full_name":
                user_data[field_name] = user.formatted_name
            elif hasattr(user, field_name):
                user_data[field_name] = getattr(user, field_name)

        # Add a fake password, or we'll get an error that the password does not match
        user_data["password"] = user_data["confirm_password"] = "fake_password"

        # See if we have a company for this user
        companies = user_api.get_user_organizations(user.id)
        if len(companies) > 0:
            company = companies[0]
            user_data["company"] = company.display_name

    except:
        user_data = None
        error = _("Invalid Activation Code")

    if request.method == 'POST':
        if "accept_terms" not in request.POST or request.POST["accept_terms"] == False:
            user_data = request.POST.copy()
            error = _("You must accept terms of service in order to continue")

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
    else:
        form = ActivationForm(user_data)

        # set focus to username field
        form.fields["password"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "user": user,
        "form": form,
        "error": error,
        "activation_code": activation_code,
        "activate_label": _("Create my McKinsey Academy account"),
        }
    return render(request, 'accounts/activate.haml', data)

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


# TODO: Implement
def access_key(request):
    pass
