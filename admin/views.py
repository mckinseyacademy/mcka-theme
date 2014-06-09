import json
from datetime import datetime
import urllib2 as url_access

from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from lib.authorization import permission_group_required
from lib.mail import sendMultipleEmails, email_add_active_student, email_add_inactive_student
from api_client.group_api import PERMISSION_GROUPS

from accounts.models import RemoteUser, UserActivation

from main.models import CuratedContentItem
from api_client import course_api
from api_client import user_api
from api_client import group_api, project_api
from api_client.json_object import Objectifier
from api_client.api_error import ApiError
from license import controller as license_controller

from .models import Client
from .models import Program
from .models import WorkGroup
from .controller import process_uploaded_student_list, get_student_list_as_file, fetch_clients_with_program, get_group_list_as_file, load_course, getStudentsWithCompanies, filterGroupsAndStudents, parse_studentslist_from_post
from .forms import ClientForm
from .forms import ProgramForm
from .forms import UploadStudentListForm
from .forms import ProgramAssociationForm
from .forms import CuratedContentItemForm




def ajaxify_http_redirects(func):
    def wrapper(*args, **kwargs):
        obj = func(*args, **kwargs)
        request = args[0]
        if request.is_ajax() and isinstance(obj, HttpResponseRedirect):
            data = { "redirect": obj.url }
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return obj

    return wrapper


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def home(request):
    return render(
        request,
        'admin/home.haml'
    )


@permission_group_required(PERMISSION_GROUPS.CLIENT_ADMIN)
def client_admin_home(request):
    return render(
        request,
        'admin/client_admin_home.haml'
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def course_meta_content_course_list(request):

    data = {
        "courses": course_api.get_course_list()
    }

    return render(
        request,
        'admin/course_meta_content/course_list.haml',
        data
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def course_meta_content_course_items(request):
    course_id = request.GET.get('course_id', None)
    items = CuratedContentItem.objects.filter(course_id=course_id).order_by('sequence')
    data = {
        "course_id": course_id,
        "items": items
    }

    return render(
        request,
        'admin/course_meta_content/item_list.haml',
        data
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def course_meta_content_course_item_new(request):
    error = None
    if request.method == "POST":
        form = CuratedContentItemForm(request.POST)
        course_id = form.data['course_id']
        if form.is_valid():
            item = form.save()
            return redirect('/admin/course-meta-content/items?course_id=%s' % course_id)
        else:
            error = "please fix the problems indicated below."
    else:
        course_id = request.GET.get('course_id', None)
        init = {'course_id': course_id}
        form = CuratedContentItemForm(initial=init)

    data = {
        "course_id": course_id,
        "form": form,
        "error": error,
        "form_action": "/admin/course-meta-content/item/new",
        "cancel_link": "/admin/course-meta-content/items?course_id=%s" % course_id
    }
    return render(
            request,
            'admin/course_meta_content/item_detail.haml',
            data
        )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def course_meta_content_course_item_edit(request, item_id):
    error = None
    item = CuratedContentItem.objects.filter(id=item_id)[0]
    if request.method == "POST":
        form = CuratedContentItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('/admin/course-meta-content/items?course_id=%s' % item.course_id)
        else:
            error = "please fix the problems indicated below."
    else:
        form = CuratedContentItemForm(instance=item)

    data = {
        "form": form,
        "error": error,
        "item": item,
        "form_action": "/admin/course-meta-content/item/%d/edit" % item.id,
        "cancel_link": "/admin/course-meta-content/items?course_id=%s" % item.course_id
    }

    return render(
        request,
        'admin/course_meta_content/item_detail.haml',
        data
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def course_meta_content_course_item_delete(request, item_id):
    item = CuratedContentItem.objects.filter(id=item_id)[0]
    # course_id = item.course_id
    item.delete()

    return redirect('/admin/course-meta-content/items?course_id=%s' % course_id)


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
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
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
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

            except ApiError as err:
                error = err.message
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


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def client_edit(request, client_id):
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        form = ClientForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                client = Client.fetch(client_id).update(client_id, request.POST)
                # Redirect after POST
                return HttpResponseRedirect('/admin/clients/')

            except ApiError as err:
                error = err.message
    else:
        ''' edit a client '''
        client = Client.fetch(client_id)
        data_dict = {'contact_name': client.contact_name, 'display_name': client.display_name, 'email': client.email, 'phone': client.phone}
        form = ClientForm(data_dict)

    # set focus to company name field
    form.fields["display_name"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "form": form,
        "client_id": client_id,
        "error": error,
        "submit_label": _("Save Client"),
    }

    return render(
        request,
        'admin/client/edit.haml',
        data
    )


def _format_upload_results(upload_results):
    results_object = Objectifier(upload_results)
    results_object.message = _("Successfully processed {} of {} records").format(
        results_object.attempted - results_object.failed,
        results_object.attempted,
    )

    return results_object


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def client_detail(request, client_id, detail_view="detail", upload_results=None):
    client = Client.fetch(client_id)
    dump(client)

    view = 'admin/client/{}.haml'.format(detail_view)

    data = {
        "client": client,
        "selected_client_tab": detail_view,
        "programs": [_prepare_program_display(program) for program in client.fetch_programs()],
    }
    if detail_view == "programs" or detail_view == "courses":
        data["students"] = client.fetch_students()
        if detail_view == "courses":
            for program in data["programs"]:
                program.courses = program.fetch_courses()
        #        for course in program.courses:
        #            users = course_api.get_users_content_filtered(course.course_id, client_id, [{'key': 'enrolled', 'value': 'True'}])
        #            course.user_count = len(users)
    if upload_results:
        data["upload_results"] = _format_upload_results(upload_results)

    return render(
        request,
        view,
        data,
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
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
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
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

            except ApiError as err:
                error = err.message

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


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def program_edit(request, program_id):
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        form = ProgramForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                program = Program.fetch(program_id).update(program_id, request.POST)
                # Redirect after POST
                return HttpResponseRedirect('/admin/programs/')

            except ApiError as err:
                error = err.message
    else:
        ''' edit a program '''
        program = Program.fetch(program_id)
        data_dict = {'name': program.name, 'display_name': program.display_name, 'start_date': program.start_date, 'end_date': program.end_date}
        form = ProgramForm(data_dict)

    # set focus to company name field
    form.fields["display_name"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "form": form,
        "program_id": program_id,
        "error": error,
        "submit_label": _("Save Client"),
    }

    return render(
        request,
        'admin/program/edit.haml',
        data
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def program_detail(request, program_id, detail_view="detail"):
    program = Program.fetch(program_id)
    view = 'admin/program/{}.haml'.format(detail_view)
    data = {
        "program": _prepare_program_display(program),
        "selected_program_tab": detail_view,
    }

    if detail_view == "detail":
        data["clients"] = fetch_clients_with_program(program.id)
    elif detail_view == "courses":
        data["courses"] = course_api.get_course_list()
        selected_ids = [course.course_id for course in program.fetch_courses()]
        for course in data["courses"]:
            course.class_name = "selected" if course.id in selected_ids else None
        data["course_count"] = len(selected_ids)

    return render(
        request,
        view,
        data,
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def upload_student_list(request, client_id):
    ''' handles requests for login form and their submission '''
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        # A form bound to the POST data and FILE data
        form = UploadStudentListForm(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass
            upload_results = process_uploaded_student_list(
                request.FILES['student_list'],
                client_id,
                request.build_absolute_uri('/accounts/activate')
            )
            return client_detail(request, client_id, detail_view="detail", upload_results=upload_results)
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


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def download_student_list(request, client_id):
    client = Client.fetch(client_id)
    filename = slugify(unicode("Student List for {} on {}".format(
        client.display_name,
        datetime.now().isoformat()
    )))

    activation_link = request.build_absolute_uri('/accounts/activate')

    response = HttpResponse(
        get_student_list_as_file(client, activation_link),
        content_type='text/csv'
    )
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
        filename
    )

    return response


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
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


def _prepare_program_display(program):
    if hasattr(program, "start_date") and hasattr(program, "end_date"):
        date_format = _('%m/%d/%Y')

        program.date_range = "{} - {}".format(
            program.start_date.strftime(date_format),
            program.end_date.strftime(date_format),
            )

    return program

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def program_association(request, client_id):
    client = Client.fetch(client_id)
    program_list = Program.list()
    error = None
    if request.method == 'POST':
        form = ProgramAssociationForm(program_list, request.POST)
        if form.is_valid():
            number_places = int(request.POST.get('places'))
            client.add_program(request.POST.get('select_program'), number_places)
            return HttpResponseRedirect('/admin/clients/{}'.format(client.id))
    else:
        form = ProgramAssociationForm(program_list)

    data = {
        "form": form,
        "client": client,
        "error": error,
        #"programs": [program for program in _prepare_program_display(program_list)],
        "programs": program_list,
    }

    return render(
        request,
        'admin/client/add_program_dialog.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def add_courses(request, program_id):
    program = Program.fetch(program_id)
    courses = request.POST.getlist("courses[]")
    for course_id in courses:
        try:
            program.add_course(course_id)
        except ApiError as e:
            # Ignore 409 errors, because they indicate a course already added
            if e.code != 409:
                raise

    return HttpResponse(
        json.dumps({"message": _("Successfully saved courses to {} program").format(program.display_name)}),
        content_type='application/json'
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def add_students_to_program(request, client_id):
    program = Program.fetch(request.POST.get("program"))
    program.courses = program.fetch_courses()
    students = request.POST.getlist("students[]")
    allocated, assigned = license_controller.licenses_report(
        program.id, client_id)
    remaining = allocated - assigned
    if len(students) > remaining:
        response = HttpResponse(
            json.dumps({"message": _("Not enough places available for {} program - {} left")
                       .format(program.display_name, remaining)}),
            content_type='application/json',
        )
        response.status_code = 403
        return response
    messages = []
    for student_id in students:
        try:
            program.add_user(client_id, student_id)
            # NEED TO CHANGE THIS ONCE MCKIN-1273 is done
            # Should do just one call to get filtered user list
            student = user_api.get_user(student_id)

            if student.is_active:
                msg = email_add_active_student(request, program, student)
            else:
                activation_record = UserActivation.get_user_activation(student)
                student.activation_code = activation_record.activation_key
                msg = email_add_inactive_student(request, program, student)
            messages.append(msg)
        except ApiError as e:
            # Ignore 409 errors, because they indicate a user already added
            if e.code != 409:
                raise
    sendMultipleEmails(messages)

    return HttpResponse(
        json.dumps({"message": _("Successfully associated students to {} program")
                   .format(program.display_name)}),
        content_type='application/json'
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def add_students_to_course(request, client_id):
    courses = request.POST.getlist("courses[]")
    students = request.POST.getlist("students[]")
    for student_id in students:
        for course_id in courses:
            try:
                user_api.enroll_user_in_course(student_id, course_id)
            except ApiError as e:
                # Ignore 409 errors, because they indicate a user already added
                if e.code != 409:
                    raise

    return HttpResponse(
        json.dumps({"message": _("Successfully associated students to courses")}),
        content_type='application/json'
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_list(request):
    ''' handles requests for login form and their submission '''

    if request.method == 'POST':
        if request.POST['select-program'] != 'select' and request.POST['select-course'] != 'select':
            return HttpResponseRedirect('/admin/workgroup/course/{}'.format(request.POST['select-course']))


    programs = Program.list()

    data = {
        "principal_name": _("Group Work"),
        "principal_name_plural": _("Group Work"),
        "principal_new_url": "/admin/workgroup/workgroup_new",
        "programs": programs,
    }

    return render(
        request,
        'admin/workgroup/list.haml',
        data
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_programs_list(request):
    ''' handles requests for login form and their submission '''

    if request.method == 'POST':
        group_id = request.POST["group_id"]
    if request.method == 'GET':
        group_id = request.GET["group_id"]

    if group_id == 'select':
        return render(
            request,
            'admin/workgroup/courses_list.haml',
            {
                "courses": {},
            }
        )
    else:
        program = Program.fetch(group_id)
        courses = program.fetch_courses()

        data = {
            "courses": courses,
        }

    return render(
        request,
        'admin/workgroup/courses_list.haml',
        data
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_course_detail(request, course_id):
    ''' handles requests for login form and their submission '''

    course = load_course(course_id)

    students, companies = getStudentsWithCompanies(course)

    if len(course.group_projects) < 1:
        return HttpResponse(json.dumps({'message': 'No group projects available for this course'}), content_type="application/json")

    groups, students = filterGroupsAndStudents(course, students)

    data = {
        "principal_name": _("Group Work"),
        "principal_name_plural": _("Group Work"),
        "course": course,
        "students": students,
        "groups": groups,
        "companies": companies.values(),
        "group_projects": course.group_projects,
    }

    return render(
        request,
        'admin/workgroup/course_detail.haml',
        data
    )

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_group_create(request, course_id):

    if request.method == 'POST':

        students, companyid, privateFlag = parse_studentslist_from_post(
            request.POST)

        course = load_course(course_id)
        if len(course.group_projects) < 1:
            return HttpResponse(json.dumps({'message': 'No group projects available for this course'}), content_type="application/json")

        groupsList = []
        privateModule = ''
        publicModule = course.group_projects[0]

        for module in course.group_projects:
            if module.name.startswith(companyid + '_'):
                privateModule = module
            groupsList = groupsList + [WorkGroup.fetch(group.group_id)
                                       for group in course_api.get_course_content_groups(course.id, module.id)]

        lastId = len(groupsList)

        if privateModule != '' and privateFlag:
            workgroup = WorkGroup.create(
                'Group {} - private - {}'.format(lastId + 1, companyid), {'privacy': 'private', 'client_id': companyid})
            group_id = int(workgroup.id)
            course_api.add_group_to_course_content(
                group_id, course_id, privateModule.id)
            workgroup.add_workgroup_to_client(companyid)
        else:
            workgroup = WorkGroup.create(
                'Group {}'.format(lastId + 1), {'privacy': 'public'})
            group_id = int(workgroup.id)
            course_api.add_group_to_course_content(
                group_id, course_id, publicModule.id)

        for student in students:
            group_api.add_user_to_group(student['id'], group_id)

        return HttpResponse(json.dumps({'message': 'Group successfully created'}), content_type="application/json")

    return HttpResponse(json.dumps({'message': 'Group wasnt created'}), content_type="application/json")

def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_project_create(request, course_id):

    if request.method == 'POST':
        print request.POST['new-project-private']
        data = {
                'private': request.POST['new-project-private'],
                'organization': request.POST['new-project-company'],
        }
        data = {}
        project = project_api.create_project(course_id, request.POST['new-project-name'], data)

        return HttpResponse(json.dumps({'message': 'Group successfully created'}), content_type="application/json")

    return HttpResponse(json.dumps({'message': 'Group wasnt created'}), content_type="application/json")



@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_group_update(request, group_id, course_id):
    if request.method == 'POST':

        students = request.POST.getlist("students[]")

        try:
            for student in students:
                group_api.add_user_to_group(student, group_id)

            return HttpResponse(json.dumps({'status': 'success'}), content_type="application/json")

        except ApiError as err:
            error = err.message
            return HttpResponse(json.dumps({'status': error}), content_type="application/json")


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_group_remove(request, group_id):

    if request.method == 'POST':

        removeStudent = request.POST['student']

        group_api.remove_user_from_group(group_id, removeStudent)

        course_id = request.POST['course_id']
        course = load_course(course_id)

        students, companies = getStudentsWithCompanies(course)

        groups, students = filterGroupsAndStudents(course, students)

        data = {
            "students": students,
        }
        return render(
            request,
            'admin/workgroup/student_table.haml',
            data,
        )

    return HttpResponse('', content_type='application/json')

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def download_group_list(request, course_id):

    course = load_course(course_id)
    groupsList = WorkGroup.list()
    groups = []
    groupedStudents = []

    for group in groupsList:
        users = group_api.get_users_in_group(group.id)
        group.students = users
        for user in users:
            companies = user_api.get_user_groups(user.id, group_type = 'organization')
            if len(companies) > 0:
                company = Client.fetch(companies[0].id)
                user.company = company.display_name
        groups.append(group)

    filename = slugify(unicode("Groups List for {} on {}".format(
        course.name,
        datetime.now().isoformat()
    )))


    response = HttpResponse(
        get_group_list_as_file(groups),
        content_type='text/csv'
    )
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
        filename
    )

    return response

def not_authorized(request):
    return render(request, 'admin/not_authorized.haml')
