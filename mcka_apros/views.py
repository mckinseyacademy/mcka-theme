import haml
import mako.template
from api_client.api_exec import get_user
from django.http import HttpResponse

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.middleware import csrf
from forms import LoginForm

import remote_auth

from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
from django.contrib.auth.models import User

from django.contrib import auth

def login(request):
    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            user = auth.authenticate(username = request.POST['username'], password = request.POST['password'])
            auth.login(request, user)
            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = LoginForm() # An unbound form
    
    template = get_haml_template('login.html.haml')
    return HttpResponse(template.render_unicode(user = None, form = form, csrf_token = csrf_token(request)))


def home(request):
    template = get_haml_template('main.html.haml')
    use_user = None
    if request.user.is_authenticated():
        use_user = request.user
    return HttpResponse(template.render_unicode(user = use_user))

# TODO: Move this to it's own helper
def get_haml_template(template_name, locations = ["templates"]):
    lookup = mako.lookup.TemplateLookup(locations, preprocessor=haml.preprocessor)

    template = lookup.get_template(template_name)

    return template

def csrf_token(context):
    """A csrf token that can be included in a form."""
    csrf_token = csrf.get_token(context)
    if csrf_token == 'NOTPROVIDED':
        return ''
    return (u'<div style="display:none"><input type="hidden"'
            ' name="csrfmiddlewaretoken" value="%s" /></div>' % (csrf_token))
