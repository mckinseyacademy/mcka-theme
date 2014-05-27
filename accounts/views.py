''' views for auth, sessions, users '''
import json
import random
from django.utils.translation import ugettext as _

from django.http import HttpResponseRedirect
from .forms import LoginForm, ActivationForm
from api_client import user_api
from .models import RemoteUser, UserActivation
from admin.models import Client

from lib.program_processor import user_program
from accounts.controller import get_current_course_for_user
from .controller import get_current_course_for_user, user_activation_with_data, ActivationError

# from importlib import import_module
# from django.conf import settings
# SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

from django.contrib import auth
import logout as logout_handler
import urllib2 as url_access

from django.shortcuts import render

import urlparse

import datetime
import math

from django.contrib.auth.decorators import login_required
VALID_USER_FIELDS = ["email", "first_name", "last_name", "full_name", "city", "country", "username", "level_of_education", "password", "is_active", "year_of_birth", "gender", "title"]

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
                    course_id = get_current_course_for_user(request)
                    if course_id:
                        redirect_to = '/courses/{}'.format(course_id)
                    else:
                        redirect_to = '/'

                return HttpResponseRedirect(redirect_to)  # Redirect after POST
            except url_access.HTTPError, err:
                error = _("An error occurred during login")
                error_messages = {
                    403: _("User account not activated"),
                    401: _("Username or password invalid"),
                    404: _("Username or password invalid"),
                }
                if err.code in error_messages:
                    error = error_messages[err.code]

                print err, error

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
        "login_label": _("Log in to my McKinsey Academy account & access my courses"),
        }
    return render(request, 'accounts/login.haml', data)

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
                user_data[field_name] = user.formatted_name()
            elif hasattr(user, field_name):
                user_data[field_name] = getattr(user, field_name)

        # Add a fake password, or we'll get an error that the password does not match
        user_data["password"] = user_data["confirm_password"] = "fake_password"

        # See if we have a company for this user
        companies = user_api.get_user_groups(user.id, Client.group_type)
        if len(companies) > 0:
            company = Client.fetch(companies[0].id)
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
            except ActivationError, activation_error:
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

def home(request):
    ''' show me the home page '''

    programData = user_program(request)
    program = programData.get('program')
    course = programData.get('course')

    data = {'popup': {'title': '', 'description': ''}}
    if request.session.get('program_popup') == None:
        if program:
            if program.id is not 'NO_PROGRAM':
                if program.start_date > datetime.datetime.today():
                    days = str(
                        int(math.floor(((program.start_date - datetime.datetime.today()).total_seconds()) / 3600 / 24))) + ' day'
                    if days > 1:
                        days = days + 's'
                    popup = {'title': '', 'description': ''}
                    popup['title'] = "Welcome to McKinsey Academy"
                    popup['description'] = "Your program will start in {}. Please explore the site to learn more about the expirience in the meantime.".format(
                        days)
                    if course:
                        popup['description'] = "Your course begins in {}. Please explore the site to learn more about the expirience in the meantime.".format(
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
def user_profile(request):
    ''' gets user_profile information in html snippet '''
    user = user_api.get_user(request.user.id)
    user_data = {
        "user_image_url": user.image_url(160),
        "user_formatted_name": user.formatted_name(),
        "user_email": user.email,
    }
    return render(request, 'accounts/user_profile.haml', user_data)
