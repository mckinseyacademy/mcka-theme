import urllib2 as url_access
import json
from datetime import datetime
from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from urllib2 import HTTPError

from lib.authorization import group_required
from .models import Client
from .models import Program
from .controller import process_uploaded_student_list, get_student_list_as_file, fetch_clients_with_program
from .forms import ClientForm
from .forms import ProgramForm
from .forms import UploadStudentListForm
from .forms import ProgramAssociationForm
from api_client import course_api
from api_client import user_api
from api_client.json_object import Objectifier


def ajaxify_http_redirects(func):
    def wrapper(request):
        obj = func(request)
        if isinstance(obj, HttpResponseRedirect):
            data = { "redirect": obj.url }
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return obj

    return wrapper


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


@ajaxify_http_redirects
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


def _format_upload_results(upload_results):
    results_object = Objectifier(upload_results)
    results_object.message = _("Successfully processed {} of {} records").format(
        results_object.attempted - results_object.failed,
        results_object.attempted,
    )

    return results_object

@group_required('super_admin')
def client_detail(request, client_id, detail_view="detail", upload_results=None):
    client = Client.fetch(client_id)
    view = 'admin/client/{}.haml'.format(detail_view)

    data = {
        "client": client,
        "selected_client_tab": detail_view,
        "programs": client.fetch_programs(),
    }

    if detail_view == "programs" or detail_view == "courses":
        data["students"] = client.fetch_students()
        if detail_view == "courses":
            for program in data["programs"]:
                program.courses = program.fetch_courses()

    if upload_results:
        data["upload_results"] = _format_upload_results(upload_results)

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


@ajaxify_http_redirects
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
def program_detail(request, program_id, detail_view="detail"):
    program = Program.fetch(program_id)
    view = 'admin/program/{}.haml'.format(detail_view)
    data = {
        "program": program,
        "selected_program_tab": detail_view,
    }

    if detail_view == "detail":
        data["clients"] = fetch_clients_with_program(program.id)
    elif detail_view == "courses":
        data["courses"] = course_api.get_course_list()
        selected_ids = [course.course_id for course in program.fetch_courses()]
        for course in data["courses"]:
            course.class_name = "selected" if course.id in selected_ids else None

    return render(
        request,
        view,
        data,
    )


@group_required('super_admin')
def upload_student_list(request, client_id):
    ''' handles requests for login form and their submission '''
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        # A form bound to the POST data and FILE data
        form = UploadStudentListForm(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass
            try:
                upload_results = process_uploaded_student_list(
                    request.FILES['student_list'],
                    client_id
                )
                return client_detail(request, client_id, detail_view="detail", upload_results=upload_results)

            except url_access.HTTPError, err:
                error = _("An error occurred during student upload")
                error_messages = {
                }
                if err.code in error_messages:
                    error = error_messages[err.code]

    else:
        ''' adds a new client '''
        form = UploadStudentListForm()  # An unbound form

    data = {
        "form": form,
        "client_id": client_id,
        "error": error,
    }

    return render(
        request,
        'admin/client/upload_list_dialog.haml',
        data
    )


@group_required('super_admin')
def download_student_list(request, client_id):
    client = Client.fetch(client_id)
    filename = "Student List for {} on {}.csv".format(
        client.display_name,
        datetime.now().isoformat()
    )

    response = HttpResponse(
        get_student_list_as_file(client),
        content_type='text/csv'
    )
    response['Content-Disposition'] = 'attachment; filename={}'.format(
        filename
    )

    return response

@group_required('super_admin')
def download_program_report(request, program_id):
    filename = "Empty Report.csv"
    response = HttpResponse(
        "Report is TBD",
        content_type='text/csv'
    )
    response['Content-Disposition'] = 'attachment; filename={}'.format(
        filename
    )

    return response


@group_required('super_admin')
def program_association(request, client_id):
    client = Client.fetch(client_id)
    program_list = Program.list()
    error = None
    if request.method == 'POST':
        form = ProgramAssociationForm(program_list, request.POST)
        if form.is_valid():
            client.add_program(request.POST.get('select_program'))
            return HttpResponseRedirect('/admin/clients/{}'.format(client.id))
    else:
        form = ProgramAssociationForm(program_list)

    data = {
        "form": form,
        "client": client,
        "error": error,
        "programs": program_list,
    }

    return render(
        request,
        'admin/client/add_program_dialog.haml',
        data
    )

@group_required('super_admin')
def add_courses(request, program_id):
    program = Program.fetch(program_id)
    courses = request.POST.getlist("courses[]")
    for course_id in courses:
        try:
            program.add_course(course_id)
        except HTTPError, e:
            # Ignore 409 errors, because they indicate a course already added
            if e.code != 409:
                raise

    return HttpResponse(
        json.dumps({"message": _("Successfully saved courses to {} program").format(program.display_name)}),
        content_type='application/json'
    )

@group_required('super_admin')
def add_students_to_program(request, client_id):
    program = Program.fetch(request.POST.get("program"))
    students = request.POST.getlist("students[]")
    for student_id in students:
        try:
            program.add_user(student_id)
        except HTTPError, e:
            # Ignore 409 errors, because they indicate a user already added
            if e.code != 409:
                raise

    return HttpResponse(
        json.dumps({"message": _("Successfully associated students to {} program").format(program.display_name)}),
        content_type='application/json'
    )

@group_required('super_admin')
def add_students_to_course(request, client_id):
    courses = request.POST.getlist("courses[]")
    students = request.POST.getlist("students[]")
    for student_id in students:
        for course_id in courses:
            try:
                user_api.enroll_user_in_course(student_id, course_id)
            except HTTPError, e:
                # Ignore 409 errors, because they indicate a user already added
                if e.code != 409:
                    raise

    return HttpResponse(
        json.dumps({"message": _("Successfully associated students to courses")}),
        content_type='application/json'
    )


def not_authorized(request):
    return render(request, 'admin/not_authorized.haml')
