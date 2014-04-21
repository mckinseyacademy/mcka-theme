from django.utils.translation import ugettext as _
from django.shortcuts import render
from lib.authorization import group_required
import urllib2 as url_access
from django.http import HttpResponseRedirect

#from api_client.admin_api import create_client, get_client_list, get_client_detail
from .models import Client
from api_client.admin_api import create_program, get_program_list, get_program_detail

from .forms import ClientForm
from .forms import ProgramForm

@group_required('super_admin')
def home(request):
    return render(
        request,
        'admin/home.haml',
        {'is_admin': True}
    )


@group_required('super_admin')
def course_meta_content(request):
    return render(
        request,
        'admin/course_meta_content.haml',
        {'is_admin': True}
    )

@group_required('super_admin')
def client_list(request):
    ''' handles requests for login form and their submission '''
    clients = Client.objects.all()
    for client in clients:
        client.detail_url = '/admin/clients/{}'.format(client.id)

    data = {
        "principal_name": _("Client"),
        "principal_name_plural": _("Clients"),
        "principal_new_url": "/admin/clients/client_new",
        "principals": clients,
        }

    return render(
        request,
        'admin/client/list.haml',
        data
    )

@group_required('super_admin')
def client_new(request):
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        form = ClientForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                client = form.save()
                return HttpResponseRedirect('/admin/clients/{}'.format(client.id))  # Redirect after POST

            except url_access.HTTPError, err:
                error = _("An error occurred during client creation")
                error_messages = {
                    403: _("You are not permitted to add new clients"),
                    401: _("Invalid data"),
                }
                if err.code in error_messages:
                    error = error_messages[err.code]
    else:
        ''' adds a new client '''
        form = ClientForm()  # An unbound form
    
    # set focus to company name field
    form.fields["name"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "form": form,
        "error": error,
        "submit_label": _("Save Client"),
        }

    return render(
        request,
        'admin/client/new.haml',
        data
    )

@group_required('super_admin')
def client_detail(request, client_id):
    client = Client.objects.get(id=client_id)

    return render(
        request,
        'admin/client/detail.haml',
        {"client": client},
    )

@group_required('super_admin')
def program_list(request):
    programs = get_program_list()
    for program in programs:
        program.detail_url = '/admin/programs/{}'.format(program.id)

    data = {
        "principal_name": _("Program"),
        "principal_name_plural": _("Programs"),
        "principal_new_url": "/admin/programs/program_new",
        "principals": programs,
        }

    return render(
        request,
        'admin/program/list.haml',
        data
    )

@group_required('super_admin')
def program_new(request):
    ''' handles requests for login form and their submission '''
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        form = ProgramForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                program = create_program(request.POST)
                return HttpResponseRedirect('/admin/programs/{}'.format(program.id))  # Redirect after POST

            except url_access.HTTPError, err:
                error = _("An error occurred during program creation")
                error_messages = {
                    403: _("You are not permitted to add new programs"),
                    401: _("Invalid data"),
                }
                if err.code in error_messages:
                    error = error_messages[err.code]
    
    else:
        ''' adds a new client '''
        form = ProgramForm()  # An unbound form
    
    # set focus to public name field
    form.fields["name"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "form": form,
        "error": error,
        "submit_label": _("Save Program"),
        }

    return render(
        request,
        'admin/program/new.haml',
        data
    )

@group_required('super_admin')
def program_detail(request, program_id):
    program = get_program_detail(program_id)

    return render(
        request,
        'admin/program/detail.haml',
        {"program": program},
    )

def not_authorized(request):
    return render(request, 'admin/not_authorized.haml')
