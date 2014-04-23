from django.utils.translation import ugettext as _
from django.shortcuts import render
from lib.authorization import group_required
import urllib2 as url_access
from django.http import HttpResponseRedirect

from .models import Client
from .models import Program

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
    clients = Client.list()
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
                name = request.POST["display_name"].lower().replace(' ', '_')
                client = Client.create(name, request.POST)
                # Redirect after POST
                return HttpResponseRedirect('/admin/clients/{}'.format(client.id))

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
    form.fields["display_name"].widget.attrs.update({'autofocus': 'autofocus'})

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
def client_detail(request, client_id, detail_view="detail"):
    client = Client.fetch(client_id)
    view = 'admin/client/{}.haml'.format(detail_view)
    data = {
        "client": client,
        "selected_client_tab": detail_view,
    }

    return render(
        request,
        view,
        data,
    )


@group_required('super_admin')
def program_list(request):
    programs = Program.list()
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
                program = Program.create(request.POST["name"], request.POST)
                # Redirect after POST
                return HttpResponseRedirect('/admin/programs/{}'.format(program.id))

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
    form.fields["display_name"].widget.attrs.update({'autofocus': 'autofocus'})

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
    program = Program.fetch(program_id)

    return render(
        request,
        'admin/program/detail.haml',
        {"program": program},
    )


def not_authorized(request):
    return render(request, 'admin/not_authorized.haml')
