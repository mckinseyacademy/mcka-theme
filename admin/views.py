import copy
import functools
import json
import re
from datetime import datetime
from time import mktime
import urllib2 as url_access
from urllib import quote as urlquote
import math

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.utils.dateformat import format
from django.core.exceptions import ValidationError
from django.core import serializers
from django.core.urlresolvers import reverse

from lib.authorization import permission_group_required
from lib.mail import sendMultipleEmails, email_add_active_student, email_add_inactive_student
from api_client.group_api import PERMISSION_GROUPS
from api_client.user_api import USER_ROLES

from accounts.models import RemoteUser, UserActivation
from accounts.controller import is_future_start, save_new_client_image

from main.models import CuratedContentItem
from api_client import course_api
from api_client import user_api
from api_client import group_api, workgroup_api, organization_api
from api_client.json_object import Objectifier, JsonObjectWithImage
from api_client.api_error import ApiError
from api_client.project_models import Project
from api_client.organization_models import Organization
from api_client.workgroup_models import Submission
from license import controller as license_controller

from .models import Client
from .models import Program
from .models import WorkGroup
from .models import WorkGroupActivityXBlock
from .models import ReviewAssignmentGroup
from .models import UserRegistrationBatch, UserRegistrationError
from .controller import get_student_list_as_file, get_group_list_as_file
from .controller import fetch_clients_with_program
from .controller import load_course
from .controller import getStudentsWithCompanies, filter_groups_and_students, parse_studentslist_from_post
from .controller import get_group_project_activities, get_group_activity_xblock
from .controller import upload_student_list_threaded
from .controller import generate_course_report, generate_program_report
from .controller import get_organizations_users_completion
from .controller import get_course_metrics_for_organization
from .controller import get_course_analytics_progress_data
from .forms import ClientForm
from .forms import ProgramForm
from .forms import UploadStudentListForm
from .forms import ProgramAssociationForm
from .forms import CuratedContentItemForm
from .forms import PermissionForm
from .forms import UploadCompanyImageForm
from .review_assignments import ReviewAssignmentProcessor, ReviewAssignmentUnattainableError
from .workgroup_reports import generate_workgroup_csv_report, WorkgroupCompletionData
from .permissions import Permissions, PermissionSaveError

from courses.controller import return_course_progress, organization_course_progress_user_list
from courses.controller import social_total, round_to_int_bump_zero
from courses.user_courses import return_course_completions_stats

def ajaxify_http_redirects(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        obj = func(*args, **kwargs)
        request = args[0]
        if request.is_ajax() and isinstance(obj, HttpResponseRedirect):
            data = { "redirect": obj.url }
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return obj

    return wrapper

def client_admin_access(func):
    '''
    Ensure company admins can view only their company.
    MCKA Admin can view all clients in the system.
    '''
    @functools.wraps(func)
    def wrapper(request, client_id=None, *args, **kwargs):
        valid_client_id = None
        if request.user.is_mcka_admin:
            valid_client_id = client_id

        # make sure client admin can access only his company
        elif request.user.is_client_admin:
            orgs = user_api.get_user_organizations(request.user.id)
            if orgs:
                valid_client_id = orgs[0].id

        if valid_client_id is None:
            raise Http404

        return func(request, valid_client_id, *args, **kwargs)

    return wrapper



@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA)
def home(request):
    return render(
        request,
        'admin/home.haml'
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_home(request, client_id):

    organization = Client.fetch(client_id)

    programs = []
    coursesIDs = []
    programsAPI = organization.fetch_programs()

    for program in programsAPI:
        program.coursesIDs = []
        program.courses = []
        for course in program.fetch_courses():
            program.coursesIDs.append(course.course_id)
            coursesIDs.append(course.course_id)
        programs.append(_prepare_program_display(program))

    coursesIDs = list(set(coursesIDs))
    courses = course_api.get_courses(course_id=coursesIDs)

    for course in courses:
        course = _prepare_course_display(course)
        course.metrics = course_api.get_course_metrics(course.id, organization=client_id)
        course.metrics.users_completed, course.metrics.percent_completed = get_organizations_users_completion(client_id, course.id, course.metrics.users_enrolled)
        for program in programs:
            if course.id in program.coursesIDs:
                program.courses.append(course)

    company_image = organization.image_url(size=48)
    data = {
        'client': organization,
        'programs': programs,
        'company_image': company_image,
        'selected_tab': 'home',
    }

    return render(
        request,
        'admin/client-admin/home.haml',
        data,
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_program_detail(request, client_id):
    # In the future, when Companies have multiple program running,
    # we will need to allow them a drop down that allows them to choose from all programs.
    program = Client.fetch(client_id).fetch_programs()[0]
    program_courses = program.fetch_courses()
    course_ids = list(set([pc.course_id for pc in program_courses]))
    courses = course_api.get_courses(course_id=course_ids)

    for course in courses:
        course.metrics = get_course_metrics_for_organization(course.id, client_id)

    total_avg_grade = 0
    total_pct_completed = 0
    if courses:
        count = float(len(courses))
        total_avg_grade = sum([c.metrics.users_grade_average for c in courses]) / count
        total_pct_completed = int(sum([c.metrics.percent_completed for c in courses]) / count)

    data = {
        'program': program,
        'courses': courses,
        'total_avg_grade': total_avg_grade,
        'total_pct_completed': total_pct_completed
    }
    return render(
        request,
        'admin/client-admin/program_detail.haml',
        data,
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_course(request, client_id, course_id):
    course = load_course(course_id)
    metrics = course_api.get_course_metrics(course_id, organization=client_id)
    metrics.users_completed, metrics.percent_completed = get_organizations_users_completion(client_id, course.id, metrics.users_enrolled)
    cutoffs = ", ".join(["{}: {}".format(k, v) for k, v in sorted(metrics.grade_cutoffs.iteritems())])

    data = {
        'client_id': client_id,
        'course_id': course_id,
        'course_info': course,
        'course_start': course.start.strftime('%m/%d/%Y') if course.start else '',
        'course_end': course.end.strftime('%m/%d/%Y') if course.end else '',
        'metrics': metrics,
        'cutoffs': cutoffs
    }
    return render(
        request,
        'admin/client-admin/course_info.haml',
        data,
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_course_participants(request, client_id, course_id):

    participants = course_api.get_users_list_in_organizations(course_id, client_id)
    total_participants = len(participants)
    if total_participants > 0:
        users_ids = [str(user.id) for user in participants]
        users_progress = organization_course_progress_user_list(course_id, client_id, count=total_participants)
        user_progress_lookup = {str(u.id):u.user_progress_display for u in users_progress}

        additional_fields = ["full_name", "title", "avatar_url"]
        students = user_api.get_users(ids=users_ids, fields=additional_fields)
        for student in students:
            student.avatar_url = student.image_url(size=48)
            student.progress = user_progress_lookup[str(student.id)] if str(student.id) in user_progress_lookup else 0
    else:
        students = []

    data = {
        'client_id': client_id,
        'course_id': course_id,
        'total_participants': total_participants,
        'students': students
    }
    return render(
        request,
        'admin/client-admin/course_participants.haml',
        data,
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def client_admin_download_course_report(request, client_id, course_id):
    filename = slugify(
        unicode(
            "{} Course Report for {} on {}".format(
                client_id,
                course_id,
                datetime.now().isoformat()
            )
        )
    ) + ".csv"

    participants = course_api.get_users_list_in_organizations(course_id, client_id)

    users_ids = [str(user.id) for user in participants]
    users_progress = organization_course_progress_user_list(course_id, client_id, count=len(participants))
    user_progress_lookup = {str(u.id):u.user_progress_display for u in users_progress}

    additional_fields = ["full_name", "title", "avatar_url"]
    students = user_api.get_users(ids=users_ids, fields=additional_fields)
    for student in students:
        student.progress = user_progress_lookup[str(student.id)] if str(student.id) in user_progress_lookup else 0

    url_prefix = "{}://{}".format(
        "https" if request.is_secure() else "http",
        request.META['HTTP_HOST']
    )

    response = HttpResponse(
        generate_course_report(client_id, course_id, url_prefix, students),
        content_type='text/csv'
    )

    response['Content-Disposition'] = 'attachment; filename={}'.format(
        filename
    )

    return response

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_download_program_report(request, client_id, program_id):
    organization = Client.fetch(client_id)
    program = organization.fetch_programs()[0]

    filename = slugify(
        unicode(
            "{} Program Report for {} on {}".format(
                client_id,
                program_id,
                datetime.now().isoformat()
            )
        )
    ) + ".csv"

    program_courses = program.fetch_courses()
    course_ids = list(set([pc.course_id for pc in program_courses]))
    courses = course_api.get_courses(course_id=course_ids)

    for course in courses:
        course.metrics = get_course_metrics_for_organization(course.id, client_id)

    total_avg_grade = 0
    total_pct_completed = 0
    if courses:
        count = float(len(courses))
        total_avg_grade = sum([c.metrics.users_grade_average for c in courses]) / count
        total_pct_completed = int(sum([c.metrics.percent_completed for c in courses]) / count)

    url_prefix = "{}://{}".format(
        "https" if request.is_secure() else "http",
        request.META['HTTP_HOST']
    )

    response = HttpResponse(
        generate_program_report(organization.name, program_id, url_prefix, courses, total_avg_grade, total_pct_completed),
        content_type='text/csv'
    )

    response['Content-Disposition'] = 'attachment; filename={}'.format(
        filename
    )

    return response


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_course_analytics(request, client_id, course_id):

    course = load_course(course_id)
    students = course_api.get_users_list_in_organizations(course_id, client_id)
    cohort_students = course_api.get_user_list(course_id)
    metrics = course_api.get_course_metrics_completions(course.id, skipleaders=True)
    average_progress = metrics.course_avg

    completed_modules = 0
    course_modules = 0
    cohort_completed_modules = 0
    cohort_course_modules = 0

    for student in students:
        student_completed, graded = return_course_completions_stats(course, student.id)
        completed_modules += student_completed
        course_modules += graded
    for student in cohort_students:
        student_completed, graded = return_course_completions_stats(course, student.id)
        cohort_completed_modules += student_completed
        cohort_course_modules += graded

    try:
        progress = float(completed_modules)/course_modules
        course.company_progress = int(progress * 100)
        course.company_progress_chart = int(5*round(progress*20))
    except ZeroDivisionError:
        course.company_progress = 0
        course.company_progress_chart = 0
    try:
        progress = float(cohort_completed_modules)/cohort_course_modules
        course.cohort_progress = int(progress * 100)
        course.cohort_progress_chart = int(5*round(progress*20))
    except ZeroDivisionError:
        course.cohort_progress = 0
        course.cohort_progress_chart = 0

    employee_engagement = course_api.get_course_social_metrics(course_id, organization_id=client_id)
    employee_point_sum = sum([social_total(user_metrics) for user_metrics in employee_engagement.users.__dict__.iteritems()])
    employee_avg = float(employee_point_sum)/employee_engagement.total_enrollments if employee_engagement.total_enrollments > 0 else 0

    course_engagement = course_api.get_course_social_metrics(course_id)
    course_point_sum = sum([social_total(user_metrics) for user_metrics in course_engagement.users.__dict__.iteritems()])
    course_avg = float(course_point_sum)/course_engagement.total_enrollments if course_engagement.total_enrollments > 0 else 0

    data = {
        'client_id': client_id,
        'course_id': course_id,
        'course': course,
        'average_progress': average_progress,
        'engagement': {
            'employee_avg': round_to_int_bump_zero(employee_avg),
            'course_avg': round_to_int_bump_zero(course_avg)
        }
    }
    return render(
        request,
        'admin/client-admin/course_analytics.haml',
        data,
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_course_analytics_participants(request, client_id, course_id):
    course = course_api.get_course(course_id)
    start_date = course.start
    end_date = course.end if course.end and course.end < datetime.today() else datetime.today()
    time_series_metrics = course_api.get_course_time_series_metrics(course_id, start_date, end_date, organization_id=client_id)
    data = {
        'modules_completed': time_series_metrics.modules_completed,
        'participants': time_series_metrics.active_users
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_course_analytics_progress(request, client_id, course_id):
    course = load_course(course_id)
    course_modules = course.components_ids(settings.PROGRESS_IGNORE_COMPONENTS)


    jsonResult = [{"key": "Your Company", "values": get_course_analytics_progress_data(course, course_modules, client_id=client_id)},
                    {"key": "Your Cohort", "values": get_course_analytics_progress_data(course, course_modules)}]
    return HttpResponse(
                json.dumps(jsonResult),
                content_type='application/json'
            )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_course_status(request, client_id, course_id):
    course = load_course(course_id)
    start_date = course.start
    end_date = datetime.now()
    if course.end is not None:
        if end_date > course.end:
            end_date = course.end
    metrics = course_api.get_course_time_series_metrics(course_id, start_date, end_date, organization_id=client_id)
    metricsJson = []
    day = 1
    week = 0
    for i, metric in enumerate(metrics.users_started):
        started = metrics.users_started[i][1]
        completed = metrics.users_completed[i][1]
        not_started = metrics.users_not_started[i][1]
        total = not_started + started + completed
        if total != 0:
            metricsJson.append({"day": (day + week * 7),
                "Not started": float(not_started) / total * 100,
                "In progress": float(started) / total * 100,
                "Completed": float(completed) / total * 100})
        else:
            metricsJson.append({"day": (day + week * 7),
                "Not started": 0,
                "In progress": 0,
                "Completed": 0})
        if day > 0 and day < 8:
            day += 1
        else:
            week += 1
            day = 1

    return HttpResponse(
                json.dumps(metricsJson),
                content_type='application/json'
            )

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def client_admin_unenroll_participant(request, client_id, course_id, user_id):
    error = None
    is_program = 'program' in request.GET
    should_confirm = 'confirm' in request.GET
    if request.method == 'POST':
        try:
            # un-enroll from program
            if is_program:
                user_api.unenroll_user_from_course(user_id, course_id)
                user_programs = Program.user_program_list(user_id)
                for program in user_programs:
                    if course_id in [course.course_id for course in program.fetch_courses()]:
                        program.remove_user(client_id, user_id)

            # un-enroll from course
            else:
                user_api.unenroll_user_from_course(user_id, course_id)

            redirect_url = "/admin/client-admin/{}/courses/{}/participants".format(client_id, course_id)
            return HttpResponseRedirect(redirect_url)
        except ApiError as err:
            error = err.message

    participant = user_api.get_user(user_id)

    data = {
        'participant': participant,
        'unenroll_course': _("Un-enroll from this course"),
        'unenroll_program': _("Un-enroll from entire program "),
        'client_id': client_id,
        'course_id': course_id,
        'is_program': is_program,
        'query': "?program" if is_program else "",
    }

    if should_confirm:
        return render(request, 'admin/client-admin/unenroll_dialog_confirm.haml', data)
    else:
        return render(request, 'admin/client-admin/unenroll_dialog.haml', data)

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def client_admin_email_not_started(request, client_id, course_id):
    students = []
    participants = course_api.get_users_list_in_organizations(course_id, client_id)
    course = load_course(course_id)
    total_participants = len(participants)
    if total_participants > 0:
        obs_users_base = [str(user.id) for user in course_api.get_users_filtered_by_role(course_id) if user.role == USER_ROLES.OBSERVER]
        users_progress = organization_course_progress_user_list(course_id, client_id, count=total_participants)
        user_progress_lookup = {str(u.id):u.user_progress_display for u in users_progress}
        users_ids = [str(p.id) for p in participants if str(p.id) not in user_progress_lookup and str(p.id) not in obs_users_base]
        additional_fields = ["full_name", "email"]
        students = user_api.get_users(ids=users_ids, fields=additional_fields)

    error = None
    if request.method == 'POST':
        user = user_api.get_user(request.user.id)
        email_header_from = user.email
        email_from = "{}<{}>".format(
            user.formatted_name,
            settings.APROS_EMAIL_SENDER
        )
        email_to = [student.email for student in students]
        email_content = request.POST["message"]
        email_subject = "Start the {} Course!".format(course.name)

        try:
            email = EmailMessage(email_subject, email_content, email_from, email_to, headers = {'Reply-To': email_header_from})
            email.send(fail_silently=False)
        except ApiError as err:
            error = err.message

        redirect_url = reverse('client_admin_course', kwargs={'client_id': client_id, 'course_id': course_id})
        return HttpResponseRedirect(redirect_url)

    data = {
        'students': students,
        'client_id': client_id,
        'course_id': course_id,
    }

    return render(request, 'admin/client-admin/email_not_started_dialog.haml', data)


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def client_admin_user_progress(request, client_id, course_id, user_id):
    userCourses = user_api.get_user_courses(user_id)
    student = user_api.get_user(user_id)
    student.avatar_url = student.image_url(size=48)
    courses = []
    for courseName in userCourses:
        course = load_course(courseName.id, depth=4)
        if course.id != course_id:
            course.progress = return_course_progress(course, user_id)
            courses.append(course)
    data = {
        'courses' : courses,
        'student' : student,
    }
    return render(
        request,
        'admin/client-admin/user_progress.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def client_admin_contact(request, client_id):
    client = Client.fetch(client_id)

    groups = Client.fetch_contact_groups(client_id)

    contacts = []
    fields = ['phone', 'full_name', 'title', 'avatar_url']

    for group in groups:
        if group.type == "contact_group":
            users = group_api.get_users_in_group(group.id)
            user_ids = [str(user.id) for user in users]
            contacts.extend(user_api.get_users(fields=fields, ids=(',').join(user_ids)))

    data = {
        'client': client,
        'contacts': contacts,
        'selected_tab': 'contact',
    }
    return render(
        request,
        'admin/client-admin/contact.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def course_meta_content_course_list(request):
    courses = course_api.get_course_list()
    for course in courses:
        course.id = urlquote(course.id)

    data = {
        "courses": courses
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
        "course_id": urlquote(course_id),
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
            return redirect('/admin/course-meta-content/items?course_id=%s' % urlquote(course_id))
        else:
            error = "please fix the problems indicated below."
    else:
        course_id = request.GET.get('course_id', None)
        init = {'course_id': course_id }
        form = CuratedContentItemForm(initial=init)

    data = {
        "course_id": urlquote(course_id),
        "form": form,
        "error": error,
        "form_action": "/admin/course-meta-content/item/new",
        "cancel_link": "/admin/course-meta-content/items?course_id=%s" % urlquote(course_id)
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
            return redirect('/admin/course-meta-content/items?course_id=%s' % urlquote(item.course_id))
        else:
            error = "please fix the problems indicated below."
    else:
        form = CuratedContentItemForm(instance=item)

    data = {
        "form": form,
        "error": error,
        "item": item,
        "form_action": "/admin/course-meta-content/item/%d/edit" % item.id,
        "cancel_link": "/admin/course-meta-content/items?course_id=%s" % urlquote(item.course_id)
    }

    return render(
        request,
        'admin/course_meta_content/item_detail.haml',
        data
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def course_meta_content_course_item_delete(request, item_id):
    item = CuratedContentItem.objects.filter(id=item_id)[0]
    course_id = urlquote(item.course_id)
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
                client_data = {k:v for k, v in request.POST.iteritems()}
                name = client_data["display_name"].lower().replace(' ', '_')
                client = Client.create(name, client_data)
                if hasattr(client, 'logo_url') and client.logo_url is not None:
                    old_image_url = client.logo_url
                    if old_image_url[:10] == '/accounts/':
                        old_image_url = old_image_url[10:]
                    elif old_image_url[:8] == '/static/':
                        prefix = 'https://' if request.is_secure() else 'http://'
                        old_image_url = prefix + request.get_host() + old_image_url
                    company_image = 'images/company_image-{}.jpg'.format(client.id)
                    save_new_client_image(old_image_url, company_image, client)

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
        "company_image": "/static/image/empty_avatar.png",
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
    client = Client.fetch(client_id)
    if request.method == 'POST':  # If the form has been submitted...
        form = ClientForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                client = Client.update_and_fetch(client_id, request.POST)
                # Redirect after POST
                return HttpResponseRedirect('/admin/clients/')

            except ApiError as err:
                error = err.message
    else:
        form = ClientForm({
            'contact_name': client.contact_name,
            'display_name': client.display_name,
            'contact_email': client.contact_email,
            'contact_phone': client.contact_phone,
            'logo_url': client.logo_url
        })

    # set focus to company name field
    form.fields["display_name"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "form": form,
        "client_id": client_id,
        "company_image": client.image_url(),
        "error": error,
        "submit_label": _("Save Client"),
    }

    return render(
        request,
        'admin/client/edit.haml',
        data
    )


def _format_upload_results(upload_results):
    upload_results.message = _("Successfully processed {} of {} records").format(
        upload_results.attempted - upload_results.failed,
        upload_results.attempted,
    )

    return upload_results

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def client_detail(request, client_id, detail_view="detail", upload_results=None):
    client = Client.fetch(client_id)

    view = 'admin/client/{}.haml'.format(detail_view)

    programs = []
    enrolledStudents = []
    for program in client.fetch_programs():
        programs.append(_prepare_program_display(program))
    data = {
        "client": client,
        "selected_client_tab": detail_view,
        "programs": programs,
    }
    if detail_view == "programs" or detail_view == "courses":
        data["students"] = client.fetch_students_by_enrolled()
        if detail_view == "courses":
            for program in data["programs"]:
                program.courses = program.fetch_courses()

        if detail_view == "programs":
            user_ids = [str(student.id) for student in data["students"]]
            additional_fields = ["created", "is_active"]
            user_dict = {str(u.id) : u for u in user_api.get_users(ids=user_ids,fields=additional_fields)} if len(user_ids) > 0 else {}
            for student in data["students"]:
                user = user_dict[str(student.id)]
                if user.created:
                    student.created = user.created.strftime(settings.SHORT_DATE_FORMAT)
                if user.is_active == True:
                    student.enrolled = True

    return render(
        request,
        view,
        data,
    )

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def client_resend_user_invite(request, client_id, user_id):
    ''' handles requests for resending student invites '''
    if request.method == 'POST':  # If the form has been submitted...
        try:
            student = user_api.get_user(user_id)
            licenses = license_controller.fetch_granted_licenses(user_id, client_id)
            client = Client.fetch(client_id)
            programs_temp = client.fetch_programs()
            programs = []
            if programs_temp and licenses:
                for program_temp in programs_temp:
                    for license in licenses:
                        if license.granted_id == program_temp.id:
                            programs.append(program_temp)
            else:
                return HttpResponse(
                    json.dumps({"status": _("This student hasn't been added to any programs yet.")}),
                    content_type='application/json'
                )
            messages = []
            activation_record = UserActivation.get_user_activation(student)
            student.activation_code = activation_record.activation_key
            for program in programs:
                messages.append(email_add_inactive_student(request, program, student))
            sendMultipleEmails(messages)
        except HTTPError, e:
            return HttpResponse(
                json.dumps({"status": _("fail")}),
                content_type='application/json'
            )
        return HttpResponse(
            json.dumps({"status": _("success")}),
            content_type='application/json'
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
            name = form.cleaned_data.get('name')
            data = {
                'display_name': form.cleaned_data.get('display_name'),
                'start_date': form.cleaned_data.get('start_date'),
                'end_date': form.cleaned_data.get('end_date'),
            }
            try:
                program = Program.fetch(program_id).update(program_id, name, data)
                # Redirect after POST
                return HttpResponseRedirect('/admin/programs/')

            except ApiError as err:
                error = err.message
    else:
        ''' edit a program '''
        program = Program.fetch(program_id)
        data_dict = {
            'name': program.name,
            'display_name': program.display_name,
            'start_date': program.start_date,
            'end_date': program.end_date
        }
        form = ProgramForm(data_dict)

    # set focus to company name field
    form.fields["display_name"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "form": form,
        "program_id": program_id,
        "error": error,
        "submit_label": _("Save Program"),
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
            course.instance = course.id.replace("slashes:", "")
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
            reg_status = UserRegistrationBatch.create();
            upload_student_list_threaded(
                request.FILES['student_list'],
                client_id,
                request.build_absolute_uri('/accounts/activate'),
                reg_status
            )
            return HttpResponse(
                json.dumps({"task_key": _(reg_status.task_key)}),
                content_type='text/plain'
            )
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
def upload_student_list_check(request, client_id, task_key):
    ''' checks on status of student list upload '''

    reg_status = UserRegistrationBatch.objects.filter(task_key=task_key)
    UserRegistrationBatch.clean_old();
    if len(reg_status) > 0:
        reg_status = reg_status[0]
        if reg_status.attempted == (reg_status.failed + reg_status.succeded):
            errors = UserRegistrationError.objects.filter(task_key=reg_status.task_key)
            errors_as_json = serializers.serialize('json', errors)
            status = _format_upload_results(reg_status)
            for error in errors:
                error.delete()
            reg_status.delete()
            return HttpResponse(
                '{"done":"done","error":' + errors_as_json + ', "message": "' + status.message + '"}',
                content_type='application/json'
            )
        else:
            return HttpResponse(
                        json.dumps({'done': 'progress',
                                    'attempted': reg_status.attempted,
                                    'failed': reg_status.failed,
                                    'succeded': reg_status.succeded}),
                        content_type='application/json'
                    )
    return HttpResponse(
            json.dumps({'done': 'failed',
                        'attempted': '0',
                        'failed': '0',
                        'succeded': '0'}),
            content_type='application/json'
        )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def download_student_list(request, client_id):
    client = Client.fetch(client_id)
    filename = slugify(
        unicode(
            "Student List for {} on {}".format(
                client.display_name,datetime.now().isoformat()
            )
        )
    )

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


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA)
def download_group_projects_report(request, course_id):
    filename = slugify(
        unicode(
            "Group Report for {} on {}".format(
                course_id,
                datetime.now().isoformat()
            )
        )
    ) + ".csv"

    url_prefix = "{}://{}".format(
        "https" if request.is_secure() else "http",
        request.META['HTTP_HOST']
    )

    response = HttpResponse(
        generate_workgroup_csv_report(course_id, url_prefix),
        content_type='text/csv'
    )

    response['Content-Disposition'] = 'attachment; filename={}'.format(
        filename
    )

    return response

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA)
def group_work_status(request, course_id, group_id=None):
    wcd = WorkgroupCompletionData(course_id, group_id)
    data = wcd.build_report_data()
    data.update({'selected_client_tab':'group_work_status'})

    template = 'admin/workgroup/workgroup_{}report.haml'.format('detail_' if group_id else '')

    return render(
        request,
        template,
        data
    )


def _prepare_program_display(program):
    if hasattr(program, "start_date") and hasattr(program, "end_date"):
        program.date_range = "{} - {}".format(
            program.start_date.strftime(settings.SHORT_DATE_FORMAT),
            program.end_date.strftime(settings.SHORT_DATE_FORMAT),
            )

    return program

def _prepare_course_display(course):
    if hasattr(course, "start") and hasattr(course, "end"):
        if is_future_start(course.start):
            course.date_range = _("Coming Soon")
        elif course.end != None and is_future_start(course.end) == False:
            course.date_range = _("Archived")
        else:
            course.date_range = course.formatted_time_span
    return course

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def program_association(request, client_id):
    client = Client.fetch(client_id)
    program_list = Program.list()
    error = None
    if request.method == 'POST':
        form = ProgramAssociationForm(program_list, request.POST)
        if form.is_valid():
            data = {k:v for k, v in request.POST.iteritems()}
            number_places = int(data.get('places'))
            client.add_program(data.get('select_program'), number_places)
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

    additional_fields = ["is_active"]
    user_dict = {str(u.id) : u for u in user_api.get_users(ids=students,fields=additional_fields)} if len(students) > 0 else {}
    for student_id in students:
        try:
            program.add_user(client_id, student_id)
            student = user_dict[student_id]

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

    if settings.ENABLE_AUTOMATIC_EMAILS_UPON_PROGRAM_ENROLLMENT:
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


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA)
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


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA)
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

class GroupProjectInfo(object):
    def __init__(self, id, name, status, organization=None, organization_id=0):
        self.id = id
        self.name = name
        self.status = status
        self.organization = organization
        self.organization_id = organization_id

def load_group_projects_info_for_course(course, companies):
    group_project_lookup = {gp.id: gp.name for gp in course.group_project_chapters}
    group_projects = []
    for project in Project.fetch_projects_for_course(course.id):
        try:
            project_name = group_project_lookup[project.content_id]
            project_status = 1
        except:
            project_name = project.content_id
            project_status = 0

        if project.organization is None:
            group_projects.append(
                GroupProjectInfo(
                    project.id,
                    project_name,
                    project_status
                )
            )
        else:
            group_projects.append(
                GroupProjectInfo(
                    project.id,
                    project_name,
                    project_status,
                    companies[project.organization].display_name,
                    companies[project.organization].id,
                )
            )

    return group_projects

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA)
def workgroup_detail(request, course_id, workgroup_id):
    '''
    Get detailed information about the specific workgroup for this course
    '''
    workgroup = WorkGroup.fetch(workgroup_id)
    additional_fields = ["avatar_url"]
    user_ids = [str(u.id) for u in workgroup.users]
    users = user_api.get_users(ids=user_ids,fields=additional_fields)
    project = Project.fetch(workgroup.project)

    course = load_course(course_id, request=request)
    projects = [gp for gp in course.group_project_chapters if gp.id == project.content_id and len(gp.sequentials) > 0]
    activities = []
    if len(projects) > 0:
        project.name = projects[0].name
        activities = get_group_project_activities(projects[0])

    submission_map = workgroup_api.get_latest_workgroup_submissions_by_id(workgroup.id, Submission)
    submissions = [v for k,v in submission_map.iteritems()]

    data = {
        "workgroup": workgroup,
        "users": users,
        "project": project,
        "activities": activities,
        "submissions": submissions
    }

    return render(
        request,
        'admin/workgroup/workgroup_detail.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA)
def workgroup_course_detail(request, course_id):
    ''' handles requests for login form and their submission '''

    selected_project_id = request.GET.get("project_id", None)
    course = load_course(course_id, request=request)

    students, companies = getStudentsWithCompanies(course)

    if len(course.group_project_chapters) < 1:
        return HttpResponse(json.dumps({'message': 'No group projects available for this course'}), content_type="application/json")

    group_projects = load_group_projects_info_for_course(course, companies)
    group_project_groups, students = filter_groups_and_students(group_projects, students)

    for project in group_projects:
        project.groups = group_project_groups[project.id]
        project.selected = (selected_project_id == str(project.id))

    data = {
        "principal_name": _("Group Work"),
        "principal_name_plural": _("Group Work"),
        "course": course,
        "students": students,
        "companies": companies.values(),
        "group_projects": group_projects,
        "selected_client_tab": "edit_groups",
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
        students = request.POST.getlist('students[]')
        project_id = request.POST['project_id']

        # load project, and make sure if private that all students are in the correct organisation
        project = Project.fetch(project_id)
        if project.organization is not None:
            organization = Organization.fetch(project.organization)
            bad_users = [u for u in students if int(u) not in organization.users]

            if len(bad_users) > 0:
                message = "Bad users {} for private project".format(
                    ",".join([u for u in bad_users])
                )
                return HttpResponse(json.dumps({'message': ''}), content_type="application/json")

        workgroups = sorted(project.workgroups)
        lastId = 0 if not workgroups else int(workgroup_api.get_workgroup(workgroups[-1]).name.split()[-1])

        workgroup = WorkGroup.create(
            'Group {}'.format(lastId + 1),
            {
                "project": project_id,
            }
        )

        workgroup.add_user_list(students)

        return HttpResponse(json.dumps({'message': 'Group successfully created'}), content_type="application/json")

    return HttpResponse(json.dumps({'message': 'Group wasnt created'}), content_type="application/json")


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_project_create(request, course_id):
    message = _("Error creating project")
    status_code = 400

    if request.method == "POST":
        project_section = request.POST["project_section"]
        organization = None
        private_project = request.POST.get("new-project-private", None)
        if private_project == "on":
            organization = request.POST["new-project-company"]

        try:
            project = Project.create(course_id, project_section, organization)
            message = _("Project successfully created")
            status_code = 200

        except ApiError as e:
            message = e.message
            status_code = e.code
    response = HttpResponse(json.dumps({"message": message}), content_type="application/json")
    response.status_code = status_code
    return response

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_remove_project(request, project_id):
    message = _("Error deleting project")
    status_code = 400

    try:
        Project.delete(project_id)
    except ApiError as e:
        message = e.message
        status_code = e.code
        response = HttpResponse(json.dumps({"message": message}), content_type="application/json")
        response.status_code = status_code
        return response

    return HttpResponse(json.dumps({"message": "Project deleted successfully."}), content_type="application/json")


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_group_update(request, group_id, course_id):
    if request.method == 'POST':

        students = request.POST.getlist("students[]")
        try:
            workgroup = WorkGroup.fetch(group_id)
            workgroup.add_user_list(students)
            return HttpResponse(json.dumps({'status': 'success'}), content_type="application/json")

        except ApiError as err:
            error = err.message
            return HttpResponse(json.dumps({'status': error}), content_type="application/json")


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def workgroup_group_remove(request, group_id):
    if request.method == 'POST':

        remove_student = request.POST['student']

        workgroup = WorkGroup.fetch(group_id)
        workgroup.remove_user(remove_student)

        course_id = request.POST['course_id']
        course = load_course(course_id, request=request)

        students, companies = getStudentsWithCompanies(course)

        group_projects = load_group_projects_info_for_course(course, companies)
        group_project_groups, students = filter_groups_and_students(group_projects, students)

        data = {
            "students": students,
        }
        return render(
            request,
            'admin/workgroup/student_table.haml',
            data,
        )

    elif request.method == 'DELETE':
        WorkGroup.delete(group_id)
        return HttpResponse(json.dumps({'status': 'success'}), content_type="application/json")

    return HttpResponse('', content_type='application/json')

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def download_group_list(request, course_id):

    course = load_course(course_id, request=request)
    students, companies = getStudentsWithCompanies(course)
    group_projects = load_group_projects_info_for_course(course, companies)
    group_project_groups, students = filter_groups_and_students(group_projects, students)

    filename = slugify(unicode("Groups List for {} on {}".format(
        course.name,
        datetime.now().isoformat()
    )))

    response = HttpResponse(
        get_group_list_as_file(group_projects, group_project_groups),
        content_type='text/csv'
    )
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
        filename
    )

    return response

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA)
def generate_assignments(request, project_id, activity_id):
    error = _("Problem generating activity review assignments")
    status_code = 400
    try:
        project = Project.fetch(project_id)

        # Fetch workgroups
        workgroups = [WorkGroup.fetch(wg) for wg in project.workgroups]
        # Get list of all users
        user_ids = []
        for wkgrp in workgroups:
            user_ids.extend(wkgrp.user_ids)

        group_xblock = WorkGroupActivityXBlock.fetch_from_activity(project.course_id, activity_id)

        rap = ReviewAssignmentProcessor(
            user_ids,
            workgroups,
            group_xblock.id,
            group_xblock.group_reviews_required_count,
            group_xblock.user_review_count
        )
        rap.distribute(request.POST.get("delete_choice", "off") == "on")
        rap.store_assignments(project.course_id)

        return HttpResponse(json.dumps({"message": _("Project review assignments allocated")}), content_type='application/json')

    except ApiError as err:
        error = err.message
        status_code = err.code

    except ReviewAssignmentUnattainableError as e:
        error = _("Not enough groups to meet review criteria")

    response = HttpResponse(json.dumps({"message": error}), content_type="application/json")
    response.status_code = status_code
    return response


def not_authorized(request):
    return render(request, 'admin/not_authorized.haml')


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def permissions(request):
    '''
    Show users within "Administrative" company, and also users that have no company association
    '''

    organizations = Organization.list()

    additional_fields = ["organizations"]
    users = []

    ADMINISTRATIVE = 0
    organization_options = [(ADMINISTRATIVE, 'ADMINISTRATIVE')]
    organization_options.extend([(org.id, org.display_name) for org in organizations if org.name != settings.ADMINISTRATIVE_COMPANY])

    org_id = int(request.GET.get('organization', ADMINISTRATIVE))

    if org_id == ADMINISTRATIVE:
        # fetch users users that have no company association
        users = user_api.get_users(has_organizations=False, fields=additional_fields)

        # fetch users in administrative company
        admin_company = next((org for org in organizations if org.name == settings.ADMINISTRATIVE_COMPANY), None)
        admin_users = []
        if admin_company and admin_company.users:
            ids = [str(id) for id in admin_company.users]
            admin_users = user_api.get_users(ids=ids,fields=additional_fields)

        users.extend(admin_users)

    else:
        org = next((org for org in organizations if org.id == org_id), None)
        if org:
            ids = [str(id) for id in org.users]
            users = user_api.get_users(ids=ids, fields=additional_fields)


    # get the groups and for each group get the list of users, then intersect them appropriately
    groups = group_api.get_groups_of_type(group_api.PERMISSION_TYPE)
    group_members = {group.name : [gu.id for gu in group_api.get_users_in_group(group.id)] for group in groups}

    for user in users:
        group_names = [g.name for g in groups]
        roles = []
        if user.id in group_members.get(PERMISSION_GROUPS.MCKA_ADMIN, []):
            roles.append(_('ADMIN'))
        if user.id in group_members.get(PERMISSION_GROUPS.MCKA_TA, []):
            roles.append(_('TA'))
        if user.id in group_members.get(PERMISSION_GROUPS.CLIENT_ADMIN, []):
            roles.append(_('COMPANY ADMIN'))
        if user.id in group_members.get(PERMISSION_GROUPS.MCKA_OBSERVER, []):
            roles.append(_('OBSERVER'))
        user.roles = ", ".join(roles)
        user.company_list = ", ".join([org.display_name for org in user.organizations])

    data = {
        'users': users,
        'organization_options': organization_options,
        'organization_id': org_id
    }
    return render(request, 'admin/permissions/list.haml', data)


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def edit_permissions(request, user_id):
    '''
    define or edit existing roles for a single user
    '''
    user = user_api.get_user(user_id)
    error = None

    permissions = Permissions(user_id)

    if request.method == 'POST':
        form = PermissionForm(permissions.courses, request.POST)
        if form.is_valid():
            per_course_roles = []
            for course in permissions.courses:
                course_roles = form.cleaned_data.get(course.id, [])
                for role in course_roles:
                    per_course_roles.append({
                        'course_id': course.id,
                        'role': role
                    })
            try:
                permissions.save(form.cleaned_data.get('permissions'), per_course_roles)
            except PermissionSaveError as err:
                error = str(err)
            else:
                return HttpResponseRedirect('/admin/permissions')
    else:
        initial_data = {
            'permissions': permissions.current_permissions
        }

        for course in permissions.courses:
            initial_data[course.id] = []
            for role in permissions.user_roles:
                if course.id == role.course_id:
                    initial_data[course.id].append(role.role)

        form = PermissionForm(permissions.courses, initial=initial_data, label_suffix='')

    data = {
        'form': form,
        'error': error,
        'user': user,
        'submit_label': _("Save")
    }
    return render(request, 'admin/permissions/edit.haml', data)

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA)
def workgroup_course_assignments(request, course_id):
    selected_project_id = request.GET.get("project_id", None)
    course = load_course(course_id)

    students, companies = getStudentsWithCompanies(course)

    if len(course.group_project_chapters) < 1:
        return HttpResponse(json.dumps({'message': 'No group projects available for this course'}), content_type="application/json")

    group_projects = Project.fetch_projects_for_course(course.id)

    for project in group_projects:
        project.selected = (selected_project_id == str(project.id))
        group_project_chapter = [ch for ch in course.group_project_chapters if ch.id == project.content_id][0]
        project.name = group_project_chapter.name
        # Needs to be a separate copy here because we'd like to distinguish when 2 projects are both using the same activities below
        project.activities = copy.deepcopy(get_group_project_activities(group_project_chapter))

        if project.organization:
            project.organization = Organization.fetch(project.organization).display_name

        project_assignment_groups = []
        for workgroup in project.workgroups:
            project_assignment_groups.extend(ReviewAssignmentGroup.list_for_workgroup(workgroup))

        for activity in project.activities:
            activity.xblock = WorkGroupActivityXBlock.fetch_from_uri(get_group_activity_xblock(activity).uri)
            activity_assignments = [pag for pag in project_assignment_groups if hasattr(pag, "xblock_id") and pag.xblock_id == activity.xblock.id]
            activity.has_assignments = (len(activity_assignments) > 0)
            activity.js_safe_id = re.sub(r'\W', '', activity.id)

    data = {
        "course": course,
        "group_projects": group_projects,
        "selected_client_tab": "assignments",
    }

    return render(
        request,
        'admin/workgroup/project_assignment.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def change_company_image(request, client_id='new', template='change_company_image', error=None, company_image="/static/image/empty_avatar.png"):
    ''' handles requests for login form and their submission '''
    if(client_id != 'new'):

        client = Organization.fetch(client_id)
        company_image = client.image_url(size=200, path='absolute')

    if '?' in company_image:
        company_image = company_image + '&' + format(datetime.now(), u'U')
    else:
        company_image = company_image + '?' + format(datetime.now(), u'U')

    form = UploadCompanyImageForm(request)  # An unbound form

    data = {
        "form": form,
        "client_id": client_id,
        "error": error,
        "company_image": company_image,
    }

    return render(
        request,
        'admin/client/{}.haml'.format(template),
        data
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def company_image_edit(request, client_id="new"):
    if request.method == 'POST':
        heightPosition = request.POST.get('height-position')
        widthPosition = request.POST.get('width-position')
        x1Position = request.POST.get('x1-position')
        x2Position = request.POST.get('x2-position')
        y1Position = request.POST.get('y1-position')
        y2Position = request.POST.get('y2-position')
        if client_id == 'new':
            CompanyImageUrl = request.POST.get('upload-image-url').split('?')[0]
        else:
            client = Organization.fetch(client_id)
            CompanyImageUrl = client.image_url(size=200, path='relative')

        from PIL import Image
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        if CompanyImageUrl[:10] == '/accounts/':
            image_url = CompanyImageUrl[10:]
        elif CompanyImageUrl[:8] == '/static/':
            prefix = 'https://' if request.is_secure() else 'http://'
            image_url = prefix + request.get_host() + CompanyImageUrl
        else:
            image_url = CompanyImageUrl

        if default_storage.exists(image_url):

            original = Image.open(default_storage.open(image_url))

            width, height = original.size   # Get dimensions
            left = int(x1Position)
            top = int(y1Position)
            right = int(x2Position)
            bottom = int(y2Position)
            cropped_example = original.crop((left, top, right, bottom))

            JsonObjectWithImage.save_profile_image(cropped_example, image_url)
        if client_id == 'new':
            return HttpResponse(json.dumps({'image_url': '/accounts/' + image_url}), content_type="application/json")
        else:
            client.logo_url = '/accounts/' + image_url
            client.update_and_fetch(client.id,  {'logo_url': '/accounts/' + image_url})
            return HttpResponse(json.dumps({'image_url': '/accounts/' + image_url, 'client_id': client.id}), content_type="application/json")

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def upload_company_image(request, client_id='new'):
    ''' handles requests for login form and their submission '''
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        # A form bound to the POST data and FILE data
        form = UploadCompanyImageForm(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass

            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            from PIL import Image

            temp_image = request.FILES['company_image']
            allowed_types = ["image/jpeg", "image/png", 'image/gif', ]
            if temp_image.content_type in allowed_types:
                if client_id == 'new':
                    company_image = 'images/company_image-{}-{}-{}.jpg'.format(client_id, request.user.id, format(datetime.now(), u'U'))
                    JsonObjectWithImage.save_profile_image(Image.open(temp_image), company_image)
                else:
                    company_image = 'images/company_image-{}.jpg'.format(client_id)
                    client = Organization.fetch(client_id)
                    JsonObjectWithImage.save_profile_image(Image.open(temp_image), company_image)
                    client.logo_url = '/accounts/' + company_image
                    client.update_and_fetch(client.id,  {'logo_url': '/accounts/' + company_image})
            else:
                error = "Error uploading file. Please try again and be sure to use an accepted file format."
            return HttpResponse(change_company_image(request=request, client_id=client_id, template='change_company_image', error=error, company_image='/accounts/' + company_image), content_type='text/html')
        else:
            error = "Error uploading file. Please try again and be sure to use an accepted file format."
            return HttpResponse(change_company_image(request, client_id, 'change_company_image', error, '/accounts/' + company_image), content_type='text/html')
    else:
        ''' adds a new image '''
        form = UploadCompanyImageForm(request)  # An unbound form

    data = {
        "form": form,
        "client_id": client_id,
        "error": error,
    }

    return render(
        request,
        'admins/clients/upload_company_image.haml',
        data
    )
