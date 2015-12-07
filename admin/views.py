import copy
import functools
import json
import string
import urlparse
from datetime import datetime
from urllib import quote as urlquote, urlencode
from operator import attrgetter
from smtplib import SMTPException

import re
import os.path
from django.conf import settings
from django.core.mail import EmailMessage, send_mass_mail
from django.core import serializers
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.template import loader, RequestContext
from django.utils.dateformat import format
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from django.views.decorators.http import require_POST

from admin.controller import get_accessible_programs, get_accessible_courses_from_program, \
    load_group_projects_info_for_course
from api_client.group_api import PERMISSION_GROUPS
from api_client.user_api import USER_ROLES
from lib.authorization import permission_group_required
from lib.mail import sendMultipleEmails, email_add_active_student, email_add_inactive_student
from accounts.models import UserActivation
from accounts.controller import is_future_start, save_new_client_image
from api_client import course_api, user_api, group_api, workgroup_api, organization_api
from api_client.api_error import ApiError
from api_client.organization_models import Organization
from api_client.project_models import Project
from api_client.workgroup_models import Submission
from courses.controller import (
    Progress, Proficiency,
    return_course_progress, organization_course_progress_user_list,
    social_total, round_to_int_bump_zero, round_to_int
)
from courses.models import FeatureFlags
from license import controller as license_controller
from main.models import CuratedContentItem
from .models import (
    Client, Program, WorkGroup, WorkGroupActivityXBlock, ReviewAssignmentGroup, ContactGroup,
    UserRegistrationBatch, UserRegistrationError, ClientNavLinks, ClientCustomization,
    AccessKey
)
from .controller import (
    get_student_list_as_file, get_group_list_as_file, fetch_clients_with_program, load_course,
    getStudentsWithCompanies, filter_groups_and_students, get_group_activity_xblock,
    upload_student_list_threaded, generate_course_report, get_organizations_users_completion,
    get_course_analytics_progress_data, get_contacts_for_client, get_admin_users, get_program_data_for_report,
    MINIMAL_COURSE_DEPTH, generate_access_key)
from .forms import (
    ClientForm, ProgramForm, UploadStudentListForm, ProgramAssociationForm, CuratedContentItemForm,
    AdminPermissionForm, BasePermissionForm, UploadCompanyImageForm,
    EditEmailForm, ShareAccessKeyForm, CreateAccessKeyForm)
from .review_assignments import ReviewAssignmentProcessor, ReviewAssignmentUnattainableError
from .workgroup_reports import generate_workgroup_csv_report, WorkgroupCompletionData
from .permissions import Permissions, PermissionSaveError


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

def permission_denied(request):
    template = loader.get_template('not_authorized.haml')
    context = RequestContext(request, {'request_path': request.path})
    return HttpResponseForbidden(template.render(context))

def make_json_error(message, code):
    response = HttpResponse(
        json.dumps({"message": message}),
        content_type='application/json'
    )
    response.status_code = code
    return response

class AccessChecker(object):
    @staticmethod
    def get_organization_for_user(user):
        try:
            return user_api.get_user_organizations(user.id, organization_object=Client)[0]
        except IndexError:
            return None

    @staticmethod
    def get_courses_for_organization(org):
        courses = []
        for program in org.fetch_programs():
            courses.extend(program.fetch_courses())

        return set(course.course_id for course in courses)

    @staticmethod
    def _do_wrapping(func, request, restrict_to_key, restrict_to_callback, *args, **kwargs):
        restrict_to_ids = []
        if request.user.is_mcka_admin:
            restrict_to_ids = None
        else:
            org = AccessChecker.get_organization_for_user(request.user)
            if org:
                restrict_to_ids = restrict_to_callback(org)

        kwargs[restrict_to_key] = restrict_to_ids

        try:
            return func(request, *args, **kwargs)
        except PermissionDenied:
            return permission_denied(request)

    @staticmethod
    def check_has_course_access(course_id, restrict_to_courses_ids):
        if restrict_to_courses_ids is not None and course_id not in restrict_to_courses_ids:
            raise PermissionDenied()

    @staticmethod
    def check_has_program_access(program_id, restrict_to_programs_ids):
        if restrict_to_programs_ids is not None and program_id not in restrict_to_programs_ids:
            raise PermissionDenied()

    @staticmethod
    def check_has_user_access(student_id, restrict_to_users_ids):
        if restrict_to_users_ids is not None and student_id not in restrict_to_users_ids:
            raise PermissionDenied()

    @staticmethod
    def program_access_wrapper(func):
        """
        Ensure restricted roles (company admin, internal admin, ta)
        can only access programs mapped to their companies.

        Note it changes function signature, passing additional parameter restrict_to_programs_ids. Due to the fact it would
        make a huge list of programs for mcka admin, if user is mcka admin restrict_to_programs_ids is None
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            restrict_to_callback = lambda org: set(program.id for program in org.fetch_programs())
            return AccessChecker._do_wrapping(
                func, request, 'restrict_to_programs_ids', restrict_to_callback, *args, **kwargs
            )

        return wrapper

    @staticmethod
    def course_access_wrapper(func):
        """
        Ensure restricted roles (company admin, internal admin, ta)
        can only access courses mapped to their companies.

        Note it changes function signature, passing additional parameter restrict_to_courses_ids. Due to the fact it
        would make a huge list of courses for mcka admin, if user is mcka admin restrict_to_courses_ids is None
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            restrict_to_callback = AccessChecker.get_courses_for_organization
            return AccessChecker._do_wrapping(
                func, request, 'restrict_to_courses_ids', restrict_to_callback, *args, **kwargs
            )

        return wrapper

    @staticmethod
    def users_access_wrapper(func):
        """
        Ensure restricted roles (company admin, internal admin, ta)
        can only access users in their companies.

        Note it changes function signature, passing additional parameter allowed_user_ids. Due to the fact it would
        make a huge list of users for mcka admin, if user is mcka admin restrict_to_users_ids is None
        """
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            restrict_to_callback = lambda org: set(user_id for user_id in org.users)
            return AccessChecker._do_wrapping(
                func, request, 'restrict_to_users_ids', restrict_to_callback, *args, **kwargs
            )

        return wrapper

    @staticmethod
    def client_admin_wrapper(func):
        """
        Ensure company admins can view only their company.
        MCKA Admin can view all clients in the system.
        """
        @functools.wraps(func)
        def wrapper(request, client_id=None, *args, **kwargs):
            valid_client_id = None
            if request.user.is_mcka_admin:
                valid_client_id = client_id

            # make sure client admin can access only his company
            elif request.user.is_client_admin or request.user.is_internal_admin:
                org = AccessChecker.get_organization_for_user(request.user)
                if org:
                    valid_client_id = org.id

            if valid_client_id is None:
                raise Http404

            return func(request, valid_client_id, *args, **kwargs)

        return wrapper

checked_course_access = AccessChecker.course_access_wrapper
checked_user_access = AccessChecker.users_access_wrapper
checked_program_access = AccessChecker.program_access_wrapper
client_admin_access = AccessChecker.client_admin_wrapper

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.INTERNAL_ADMIN)
def home(request):
    return render(
        request,
        'admin/home.haml'
    )

@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN
)
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
    program, courses, total_avg_grade, total_pct_completed = get_program_data_for_report(client_id)

    data = {
        'program_info': program,
        'courses': courses,
        'total_avg_grade': total_avg_grade,
        'total_pct_completed': total_pct_completed
    }
    return render(
        request,
        'admin/client-admin/program_detail.haml',
        data,
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
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

def get_user_metrics_from_lookup(user_id, lookup):
    return lookup[user_id] if user_id in lookup else 0

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def client_admin_course_participants(request, client_id, course_id):
    course = load_course(course_id)
    users = course_api.get_users_list_in_organizations(course_id, client_id)
    obs_users_base = [user.id for user in course_api.get_users_filtered_by_role(course_id) if user.role == USER_ROLES.OBSERVER]
    total_users = len(users)
    if total_users > 0:
        users_ids = [str(user.id) for user in users if user.id not in obs_users_base]
        users_progress = organization_course_progress_user_list(course_id, client_id, count=total_users)
        user_progress_lookup = {str(u.id):u.user_progress_display for u in users_progress}

        course_proficiency = organization_api.get_users_by_enrolled(client_id, course_id=course_id, include_complete_status=True, include_grades=True)
        user_grade_lookup = {str(u.id):[round_to_int(100 * u.grade), u.complete_status] for u in course_proficiency}

        additional_fields = ["full_name", "title", "avatar_url"]
        students = user_api.get_users(ids=users_ids, fields=additional_fields)
        for student in students:
            student.avatar_url = student.image_url(size=48)
            student.progress = get_user_metrics_from_lookup(str(student.id), user_progress_lookup)
            student.proficiency, student.completed = get_user_metrics_from_lookup(str(student.id), user_grade_lookup)

    else:
        students = []

    data = {
        'client_id': client_id,
        'course_id': course_id,
        'target_course': course,
        'total_participants': len(students),
        'students': students
    }
    return render(
        request,
        'admin/client-admin/course_participants.haml',
        data,
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
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

    users = course_api.get_users_list_in_organizations(course_id, client_id)
    obs_users_base = [user.id for user in course_api.get_users_filtered_by_role(course_id) if user.role == USER_ROLES.OBSERVER]

    users_ids = [str(user.id) for user in users if user.id not in obs_users_base]
    users_progress = organization_course_progress_user_list(course_id, client_id, count=len(users))

    user_progress_lookup = {str(u.id):u.user_progress_display for u in users_progress}

    course_social_metrics = course_api.get_course_social_metrics(course_id, organization_id=client_id)
    user_social_lookup = {str(u_id):social_total(user_metrics) for u_id, user_metrics in course_social_metrics.users.__dict__.iteritems()}

    course_proficiency = organization_api.get_users_by_enrolled(client_id, course_id=course_id, include_complete_status=True, include_grades=True)
    user_grade_lookup = {str(u.id):[round_to_int(100 * u.grade), u.complete_status] for u in course_proficiency}

    additional_fields = ["full_name", "title", "avatar_url"]
    students = user_api.get_users(ids=users_ids, fields=additional_fields)
    for student in students:
        student.progress = get_user_metrics_from_lookup(str(student.id), user_progress_lookup)
        student.engagement = get_user_metrics_from_lookup(str(student.id), user_social_lookup)
        student.proficiency, completed = get_user_metrics_from_lookup(str(student.id), user_grade_lookup)
        student.completed = "Y" if completed else "N"

    students.sort(key = attrgetter('progress'), reverse = True)

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
    program, courses, total_avg_grade, total_pct_completed = get_program_data_for_report(client_id, program_id)
    filename = slugify(
        unicode(
            "{} Program Report for {} on {}".format(
                client_id,
                program_id,
                datetime.now().isoformat()
            )
        )
    ) + ".csv"
    data = {
        'client_name': organization.name,
        'program_id': program_id,
        'courses': courses,
        'total_avg_grade': total_avg_grade,
        'total_pct_completed': total_pct_completed
    }
    response = render(request, 'admin/client-admin/program_report.txt', data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    return response

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_course_analytics(request, client_id, course_id):

    course = load_course(course_id)
    (features, created) = FeatureFlags.objects.get_or_create(course_id=course_id)

    # progress
    cohort_metrics = course_api.get_course_metrics_completions(course.id, skipleaders=True, completions_object_type=Progress)
    course.cohort_progress = cohort_metrics.course_average_display

    company_metrics = course_api.get_course_metrics_completions(course.id, organizations=client_id, skipleaders=True, completions_object_type=Progress)
    course.company_progress = company_metrics.course_average_display

    # proficiency
    company_proficiency = organization_api.get_grade_complete_count(client_id, courses=course_id)
    course_proficiency = course_api.get_course_metrics_grades(course_id, grade_object_type=Proficiency)

    # engagement
    employee_engagement = course_api.get_course_social_metrics(course_id, organization_id=client_id)
    employee_point_sum = sum([social_total(user_metrics[1]) for user_metrics in employee_engagement.users.__dict__.iteritems()])
    employee_avg = float(employee_point_sum)/employee_engagement.total_enrollments if employee_engagement.total_enrollments > 0 else 0

    course_engagement = course_api.get_course_social_metrics(course_id)
    course_point_sum = sum([social_total(user_metrics[1]) for user_metrics in course_engagement.users.__dict__.iteritems()])
    course_avg = float(course_point_sum)/course_engagement.total_enrollments if course_engagement.total_enrollments > 0 else 0

    data = {
        'course': course,
        'company_proficiency': company_proficiency.users_grade_average * 100,
        'company_proficiency_graph': int(5 * round(company_proficiency.users_grade_average * 20)),
        'cohort_proficiency_graph': int(5 * round(course_proficiency.course_average_value * 20)),
        'cohort_proficiency': course_proficiency.course_average_display,
        'company_engagement': round_to_int_bump_zero(employee_avg),
        'cohort_engagement': round_to_int_bump_zero(course_avg),
        'client_id': client_id,
        'course_id': course_id,
        "feature_flags": features,
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
    time_series_metrics = course_api.get_course_time_series_metrics(course_id, start_date, end_date, organization=client_id)
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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def client_admin_course_status(request, client_id, course_id):
    course = load_course(course_id)
    start_date = course.start
    end_date = datetime.now()
    if course.end is not None:
        if end_date > course.end:
            end_date = course.end
    metrics = course_api.get_course_time_series_metrics(course_id, start_date, end_date, organization=client_id)
    metricsJson = []
    completed = 0
    started = 0
    for i, metric in enumerate(metrics.users_started):
        started += metrics.users_started[i][1]
        completed += metrics.users_completed[i][1]
        not_started = metrics.users_not_started[i][1]
        total = not_started + started
        if total != 0:
            metricsJson.append(
                {
                    "day": i + 1,
                    "Not started": float(not_started) / total * 100,
                    "In progress": float(started - completed) / total * 100,
                    "Completed": float(completed) / total * 100
                }
            )
        else:
            metricsJson.append(
                {
                    "day": i + 1,
                    "Not started": 0,
                    "In progress": 0,
                    "Completed": 0
                }
            )

    return HttpResponse(
        json.dumps(metricsJson),
        content_type='application/json'
    )

def _remove_student_from_course(student_id, course_id):
    # Mark this student as an observer for this course, so that their data is ignored in roll-up activities
    permissions = Permissions(student_id)
    permissions.add_course_role(course_id, USER_ROLES.OBSERVER)
    user_api.unenroll_user_from_course(student_id, course_id)

@ajaxify_http_redirects
@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN
)
def client_admin_edit_email(request, client_id, course_id, user_id):
    """
    Supplies a modal for editing a user's email address.
    """
    error = None
    student = user_api.get_user(user_id)
    form = EditEmailForm()
    if request.method == 'POST':
        form = EditEmailForm(data=request.POST)
        if form.is_valid():
            try:
                user_api.update_user_information(user_id, {'email': form.cleaned_data['email']})
                redirect_url = "/admin/client-admin/{}/courses/{}/participants".format(client_id, course_id)
                return HttpResponseRedirect(redirect_url)
            except ApiError as err:
                error = err.message

    data = {
        'student': student,
        'edit_email': _("Edit Email"),
        'form': form,
        'client_id': client_id,
        'course_id': course_id,
        'error': error,
    }

    return render(request, 'admin/client-admin/edit_email_modal.haml', data)

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def client_admin_unenroll_participant(request, client_id, course_id, user_id):
    error = None
    is_program = 'program' in request.GET
    should_confirm = 'confirm' in request.GET
    if request.method == 'POST':
        try:
            # un-enroll from program
            if is_program:
                _remove_student_from_course(user_id, course_id)
                user_programs = Program.user_program_list(user_id)
                for program in user_programs:
                    if course_id in [course.course_id for course in program.fetch_courses()]:
                        program.remove_user(client_id, user_id)

            # un-enroll from course
            else:
                _remove_student_from_course(user_id, course_id)

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

@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN
)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def client_admin_user_progress(request, client_id, course_id, user_id, restrict_to_courses_ids=None):
    userCourses = user_api.get_user_courses(user_id)
    student = user_api.get_user(user_id)
    student.avatar_url = student.image_url(size=48)
    courses = []
    grades = {grade.course_id: grade for grade in user_api.get_user_grades(user_id)}
    for courseName in userCourses:
        course = load_course(courseName.id, depth=MINIMAL_COURSE_DEPTH)
        if (restrict_to_courses_ids is not None) and (course.id not in restrict_to_courses_ids):
            continue
        if course.id != course_id:
            grade = grades.get(course.id, None)
            if grade:
                course.completed = grade.complete_status
                course.progress = return_course_progress(course, user_id)
            else:
                course.completed = False
                course.progress = 0
            courses.append(course)
    data = {
        'courses': courses,
        'student': student,
    }
    return render(
        request,
        'admin/client-admin/user_progress.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_contact(request, client_id):
    client = Client.fetch(client_id)

    contacts = get_contacts_for_client(client_id)

    data = {
        'client': client,
        'contacts': contacts,
        'selected_tab': 'contact',
        'view_type': 'client',
    }
    return render(
        request,
        'admin/client-admin/contact.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def course_meta_content_course_list(request, restrict_to_courses_ids=None):
    courses = course_api.get_course_list(ids=restrict_to_courses_ids)
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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def course_meta_content_course_items(request, course_id, restrict_to_courses_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)
    (features, created) = FeatureFlags.objects.get_or_create(course_id=course_id)

    items = CuratedContentItem.objects.filter(course_id=course_id).order_by('sequence')
    data = {
        "course_id": urlquote(course_id),
        "items": items,
        "feature_flags": features,
    }

    return render(
        request,
        'admin/course_meta_content/item_list.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def course_meta_content_course_item_new(request, restrict_to_courses_ids=None):
    error = None
    if request.method == "POST":
        form = CuratedContentItemForm(request.POST)
        course_id = form.data['course_id']
        AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)
        if form.is_valid():
            item = form.save()
            return redirect('/admin/course-meta-content/items/%s' % urlquote(course_id))
        else:
            error = "please fix the problems indicated below."
    else:
        course_id = request.GET.get('course_id', None)
        AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)
        init = {'course_id': course_id}
        form = CuratedContentItemForm(initial=init)

    data = {
        "course_id": urlquote(course_id),
        "form": form,
        "error": error,
        "form_action": "/admin/course-meta-content/item/new",
        "cancel_link": "/admin/course-meta-content/items/%s" % urlquote(course_id)
    }
    return render(
            request,
            'admin/course_meta_content/item_detail.haml',
            data
        )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def course_meta_content_course_item_edit(request, item_id, restrict_to_courses_ids=None):
    error = None
    item = CuratedContentItem.objects.filter(id=item_id)[0]
    AccessChecker.check_has_course_access(item.course_id, restrict_to_courses_ids)
    if request.method == "POST":
        form = CuratedContentItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('/admin/course-meta-content/items/%s' % urlquote(item.course_id))
        else:
            error = "please fix the problems indicated below."
    else:
        form = CuratedContentItemForm(instance=item)

    data = {
        "form": form,
        "error": error,
        "item": item,
        "form_action": "/admin/course-meta-content/item/%d/edit" % item.id,
        "cancel_link": "/admin/course-meta-content/items/%s" % urlquote(item.course_id)
    }

    return render(
        request,
        'admin/course_meta_content/item_detail.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def course_meta_content_course_item_delete(request, item_id, restrict_to_courses_ids=None):
    item = CuratedContentItem.objects.filter(id=item_id)[0]
    AccessChecker.check_has_course_access(item.course_id, restrict_to_courses_ids)
    course_id = urlquote(item.course_id)
    item.delete()

    return redirect('/admin/course-meta-content/items/%s' % course_id)

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def client_list(request):
    ''' handles requests for login form and their submission '''
    clients = Client.list()
    if not request.user.is_mcka_admin:
        target_id = AccessChecker.get_organization_for_user(request.user).id
        clients = [
            client for client in clients
            if client.id == target_id
        ]
    for client in clients:
        client.detail_url = '/admin/clients/{}'.format(client.id)

    data = {
        "principal_name": _("Client"),
        "principal_name_plural": _("Clients"),
        "principal_new_url": "/admin/clients/client_new",
        "principals": clients,
        "read_only": not request.user.is_mcka_admin,
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
    company_image = "/static/image/empty_avatar.png"
    if request.method == 'POST':  # If the form has been submitted...
        form = ClientForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                client_data = {k:v for k, v in request.POST.iteritems()}
                name = client_data["display_name"].lower().replace(' ', '_')
                client = Client.create(name, client_data)
                # save identity provider
                (customization, created) = ClientCustomization.objects.get_or_create(
                    client_id=client.id
                )
                customization.identity_provider = form.cleaned_data['identity_provider']
                customization.save()
                # save logo
                if hasattr(client, 'logo_url') and client.logo_url:
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
            if request.POST['logo_url']:
                company_image = request.POST['logo_url']
    else:
        ''' adds a new client '''
        form = ClientForm()  # An unbound form

    # set focus to company name field
    form.fields["display_name"].widget.attrs.update({'autofocus': 'autofocus'})

    data = {
        "form": form,
        "error": error,
        "submit_label": _("Save Client"),
        "company_image": company_image,
    }

    return render(
        request,
        'admin/client/new.haml',
        data
    )

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def client_edit(request, client_id):
    error = None
    client = Client.fetch(client_id)
    (customization, created) = ClientCustomization.objects.get_or_create(
        client_id=client_id,
    )

    if request.method == 'POST':  # If the form has been submitted...
        form = ClientForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                client = Client.update_and_fetch(client_id, request.POST)
                customization.identity_provider = form.cleaned_data['identity_provider']
                customization.save()
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
            'logo_url': client.logo_url,
            'identity_provider': customization.identity_provider,
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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
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
        # convert all of the date strings to SHORT FORMAT
        for student in data["students"]:
            student.created = datetime.strptime(student.created, "%Y-%m-%dT%H:%M:%SZ" ).strftime(settings.SHORT_DATE_FORMAT)

        if detail_view == "courses":
            for program in data["programs"]:
                program.courses = program.fetch_courses()

    return render(
        request,
        view,
        data,
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def client_detail_contact(request, client_id):

    client = Client.fetch(client_id)

    contacts = get_contacts_for_client(client_id)

    data = {
        'client': client,
        'contacts': contacts,
        'view_type': 'admin',
        'selected_client_tab': 'contact',
    }

    return render(
        request,
        'admin/client/contact.haml',
        data,
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def client_detail_navigation(request, client_id):
    client = Client.fetch(client_id)

    (customization, created) = ClientCustomization.objects.get_or_create(
        client_id=client_id,
    )
    nav_links = ClientNavLinks.objects.filter(client_id=client_id)
    nav_links = dict((link.link_name, link) for link in nav_links)

    data = {
        'client': client,
        'nav_links': nav_links,
        'customization': customization,
        'selected_client_tab': 'navigation',
    }

    return render(
        request,
        'admin/client/navigation.haml',
        data,
    )

@require_POST
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def client_detail_nav_links(request, client_id):
    for i in range(1, 7):
        link_name = request.POST['name_%s' % i]
        link_label = request.POST['label_%s' % i]
        link_url = request.POST['link_%s' % i]
        if link_label or link_url:
            (link, created) = ClientNavLinks.objects.get_or_create(
                    client_id=client_id,
                    link_name=link_name,
            )
            link.link_label = link_label or link_name
            link.link_url = link_url
            link.save()
        if not link_label and not link_url:
            ClientNavLinks.objects.filter(client_id=client_id, link_name=link_name).delete()

    return HttpResponseRedirect('/admin/clients/{}/navigation'.format(client_id))

@require_POST
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def client_detail_customization(request, client_id):
    (customization, created) = ClientCustomization.objects.get_or_create(
        client_id=client_id,
    )
    if request.FILES:
        temp_image = request.FILES['client_logo']
        allowed_types = ["image/jpeg", "image/png", 'image/gif']
        if temp_image and temp_image.content_type in allowed_types:
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            from PIL import Image

            extension = os.path.splitext(temp_image.name)[1]
            logo_url = 'images/' + settings.TEMP_IMAGE_FOLDER + 'client_logo-{}{}'.format(client_id, extension)
            default_storage.save(logo_url, ContentFile(temp_image.read()))
            customization.client_logo = logo_url

    customization.hex_notification = request.POST['hex_notification']
    customization.hex_notification_text = request.POST['hex_notification_text']
    customization.hex_background_bar = request.POST['hex_background_bar']
    customization.hex_program_name = request.POST['hex_program_name']
    customization.hex_navigation_icons = request.POST['hex_navigation_icons']
    customization.hex_course_title = request.POST['hex_course_title']
    customization.hex_page_background = request.POST['hex_page_background']
    customization.save()

    return HttpResponseRedirect('/admin/clients/{}/navigation'.format(client_id))

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def client_detail_add_contact(request, client_id):

    error = None
    client = Client.fetch(client_id)
    contacts = get_contacts_for_client(client_id)
    contact_ids = [contact.id for contact in contacts]

    if request.method == 'POST':
        contact_groups = Client.fetch_contact_groups(client_id)
        if len(contact_groups) == 0:
            contact_group = ContactGroup.create(('Contact Group - ' + str(client_id)), {})
            client.add_group(contact_group.id)
        else:
            contact_group = contact_groups[0]
        selected_users =request.POST.getlist('checks[]')
        for user in selected_users:
            try:
                group_api.add_user_to_group(user, contact_group.id)
            except ApiError as err:
                error = err.message

        if error == None:
            return HttpResponseRedirect('/admin/clients/{}/contact'.format(client_id))

    organizations = Organization.list()
    ADMINISTRATIVE = 0
    org_id = 0
    admin_users = get_admin_users(organizations, org_id, ADMINISTRATIVE)
    users = [user for user in admin_users if user.id not in contact_ids]

    data = {
        'client': client,
        'contacts': contacts,
        'users': users,
        'error': error,
    }

    return render(
        request,
        'admin/client/add_contact.haml',
        data,
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def client_detail_remove_contact(request, client_id, user_id):

    contact_group = Client.fetch_contact_groups(client_id)[0]
    try:
        group_api.remove_user_from_group(user_id, contact_group.id)
    except ApiError as err:
        return HttpResponse(
            json.dumps({"status": err.message}),
            content_type='application/json'
        )

    return HttpResponse(
        json.dumps({"status": _("Contact has been removed.")}),
        content_type='application/json'
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def access_key_list(request, client_id):

    def build_instance_name(program_id, course_id):
        instance = ""
        if program_id:
            if program_id in programs:
                instance = programs.get(program_id)
                if course_id:
                    program = Program(dictionary={'id': program_id})
                    courses = {c.course_id: c.course_id for c in program.fetch_courses()}
                    instance += ": {}".format(courses.get(course_id, _("Invalid Course Run")))
            else:
                instance = _("Invalid Program ID")
        return instance

    client = Client.fetch(client_id)
    programs = {p.id: p.name for p in client.fetch_programs()}
    access_keys = list(AccessKey.objects.filter(client_id=client_id))

    for key in access_keys:
        key.instance = build_instance_name(key.program_id, key.course_id)
        key.link = request.build_absolute_uri(reverse('access_key', kwargs={'code': key.code}))

    data = {
        'client': client,
        'access_keys': access_keys,
        'selected_client_tab': 'access_key_list',
    }

    return render(
        request,
        'admin/client/access_key_list',
        data,
    )


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def create_access_key(request, client_id):
    courses = []

    if request.method == 'POST':  # If the form has been submitted...
        if 'program_change' in request.POST: # A program is selected - skip validation
            form = CreateAccessKeyForm(initial=request.POST.dict())
        else:
            form = CreateAccessKeyForm(request.POST) # A form bound to the POST data

        # Load course choices for program
        program_id = int(request.POST.get('program_id'))
        if program_id:
            program = Program(dictionary={"id": program_id})
            courses = [(c.course_id, c.course_id) for c in program.fetch_courses()]

        if form.is_valid():  # All validation rules pass
            code = generate_access_key()
            model = form.save(commit=False)
            model.client_id = int(client_id)
            model.code = code
            model.save()
            return HttpResponseRedirect('/admin/clients/{}/access_keys'.format(client_id))
    else:
        form = CreateAccessKeyForm()

    client = Client.fetch(client_id)
    programs = [(p.id, p.display_name) for p in client.fetch_programs()]
    form.fields['program_id'].widget.choices = [(0, _('- Select -'))] + programs
    form.fields['course_id'].widget.choices = [('', _('- Select -'))] + courses

    data = {
        'form': form,
        'course': {"course_id": 0},
        'submit_label': _('Save'),
    }
    return render(request, 'admin/client/create_access_key', data)


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def share_access_key(request, client_id, access_key_id):
    error = None
    access_key = AccessKey.objects.get(pk=access_key_id)

    if request.method == 'POST':  # If the form has been submitted...
        form = ShareAccessKeyForm(request.POST.copy()) # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # @TODO Missing copy
            subject = _('Access Key')
            message = form.cleaned_data['message']
            message += '\r\n\r\n{}'.format(form.cleaned_data['access_key_link'])
            sender = settings.APROS_EMAIL_SENDER
            mails = [(subject, message, sender, [recipient]) for recipient in form.cleaned_data['recipients']]
            try:
                send_mass_mail(mails, fail_silently=False)
            except SMTPException as e:
                error = e.message
            else:
                return HttpResponseRedirect('/admin/clients/{}/access_keys'.format(client_id))
    else:
        # An unbound form
        link = request.build_absolute_uri(reverse('access_key', kwargs={'code': access_key.code}))
        form = ShareAccessKeyForm(initial={'access_key_link': link})
        form.fields['access_key_link'].widget.attrs.update({'class': 'radius'})

    data = {
        'error': error,
        'form': form,
        'access_key': access_key,
        'submit_label': _('Send'),
    }
    return render(request, 'admin/client/share_access_key.haml', data)


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def upload_student_list_check(request, client_id, task_key):
    ''' checks on status of student list upload '''

    reg_status = UserRegistrationBatch.objects.filter(task_key=task_key)
    UserRegistrationBatch.clean_old()
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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def download_student_list(request, client_id):
    client = Client.fetch(client_id)
    filename = slugify(
        unicode(
            "Student List for {} on {}".format(
                client.display_name, datetime.now().isoformat()
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

    selected_ids = [course.course_id for course in program.fetch_courses()]

    for course_id in [c for c in courses if c not in selected_ids]:
        try:
            program.add_course(course_id)
        except ApiError as e:
            # Ignore 409 errors, because they indicate a course already added
            if e.code != 409:
                raise

    for course_id in selected_ids:
        if course_id not in courses:
            try:
                program.remove_course(course_id)
            except ApiError as e:
                message = e.message
                status_code = e.code

    return HttpResponse(
        json.dumps({"message": _("Successfully saved courses to {} program").format(program.display_name)}),
        content_type='application/json'
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_program_access  # note this decorator changes method signature by adding restrict_to_programs_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
@client_admin_access
def add_students_to_program(request, client_id, restrict_to_programs_ids=None, restrict_to_users_ids=None):
    program_id = request.POST.get("program")
    try:
        program_id = int(program_id)
    except (ValueError, TypeError):
        return make_json_error(_("Invalid program_id specified: {}").format(program_id), 400)
    AccessChecker.check_has_program_access(program_id=program_id, restrict_to_programs_ids=restrict_to_programs_ids)
    program = Program.fetch(program_id)
    program.courses = program.fetch_courses()
    students = request.POST.getlist("students[]")
    try:
        if restrict_to_users_ids is not None:
            students = [student_id for student_id in students if int(student_id) in restrict_to_users_ids]
    except ValueError:
        return make_json_error(_("Invalid student_id specified: {}").format(student_id), 400)
    allocated, assigned = license_controller.licenses_report(
        program.id, client_id)
    remaining = allocated - assigned
    if len(students) > remaining:
        return make_json_error(
            _("Not enough places available for {} program - {} left").format(program.display_name, remaining), 403
        )
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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def add_students_to_course(request, client_id, restrict_to_users_ids=None, restrict_to_courses_ids=None):

    def enroll_user_in_course(user_id, course_id):
        try:
            user_api.enroll_user_in_course(user_id, course_id)
        except ApiError as e:
            # Ignore 409 errors, because they indicate a user already added
            if e.code != 409:
                raise

    courses = request.POST.getlist("courses[]")
    if restrict_to_courses_ids is not None:
        courses = [course_id for course_id in courses if course_id in restrict_to_courses_ids]
    students = [int(u_id) for u_id in request.POST.getlist("students[]")]
    if restrict_to_users_ids is not None:
        students = [u_id for u_id in students if u_id in restrict_to_users_ids]
    exception_messages = []
    for course_id in courses:
        enrolled_users = {u.id:u.username for u in course_api.get_user_list(course_id) if u.id in students}
        for student_id in students:
            if student_id in enrolled_users:
                exception_messages.append(_("{} already enrolled in {}").format(
                    enrolled_users[student_id],
                    course_id
                ))
            else:
                enroll_user_in_course(student_id, course_id)

    message = _("Successfully associated students to courses")
    if len(exception_messages) > 0:
        message = _("Successfully associated students to courses, with {} messages:\n\t{}").format(
            len(exception_messages),
            "\n\t".join(exception_messages),
        )

    return HttpResponse(
        json.dumps({"message": message}),
        content_type='application/json'
    )


def not_authorized(request):
    return render(request, 'admin/not_authorized.haml')

@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN,
    PERMISSION_GROUPS.INTERNAL_ADMIN
)
@client_admin_access
def change_company_image(request, client_id='new', template='change_company_image', error=None, company_image=None):
    ''' handles requests for login form and their submission '''
    if(client_id == 'new' and not company_image):
        company_image = "/static/image/empty_avatar.png"
    elif not company_image:
        client = Organization.fetch(client_id)
        company_image = client.image_url(size=None, path='absolute')

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

@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN,
    PERMISSION_GROUPS.INTERNAL_ADMIN
)
@client_admin_access
def company_image_edit(request, client_id="new"):
    if request.method == 'POST':
        heightPosition = request.POST.get('height-position')
        widthPosition = request.POST.get('width-position')
        x1Position = request.POST.get('x1-position')
        x2Position = request.POST.get('x2-position')
        y1Position = request.POST.get('y1-position')
        y2Position = request.POST.get('y2-position')
        CompanyImageUrl = urlparse.urlparse(request.POST.get('upload-image-url'))[2].split('?')[0]

        if client_id != 'new':
            client = Organization.fetch(client_id)

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

        image_url = image_url[1:] if image_url[0] == '/' else image_url
        new_image_url = image_url

        if default_storage.exists(image_url):

            original = Image.open(default_storage.open(image_url))

            width, height = original.size   # Get dimensions
            left = int(x1Position)
            top = int(y1Position)
            right = int(x2Position)
            bottom = int(y2Position)
            cropped_example = original.crop((left, top, right, bottom))
            new_image_url = string.replace(image_url, settings.TEMP_IMAGE_FOLDER, '')
            Organization.save_profile_image(cropped_example, image_url, new_image_url=new_image_url)

        if client_id == 'new':
            return HttpResponse(json.dumps({'image_url': '/accounts/' + new_image_url}), content_type="application/json")
        else:
            client.logo_url = '/accounts/' + new_image_url
            client.update_and_fetch(client.id,  {'logo_url': '/accounts/' + new_image_url})
            return HttpResponse(json.dumps({'image_url': '/accounts/' + new_image_url, 'client_id': client.id}), content_type="application/json")

@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN,
    PERMISSION_GROUPS.INTERNAL_ADMIN
)
@client_admin_access
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
                    company_image = 'images/' + settings.TEMP_IMAGE_FOLDER + 'company_image-{}-{}-{}.jpg'.format(client_id, request.user.id, format(datetime.now(), u'U'))
                    Organization.save_profile_image(Image.open(temp_image), company_image)
                else:
                    company_image = 'images/' + settings.TEMP_IMAGE_FOLDER + 'company_image-{}.jpg'.format(client_id)
                    Organization.save_profile_image(Image.open(temp_image), company_image)
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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_TA)
@checked_program_access  # note this decorator changes method signature by adding restrict_to_programs_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def groupwork_dashboard(request, restrict_to_programs_ids=None, restrict_to_users_ids=None):

    template = 'admin/workgroup/dashboard.haml'

    program_id = request.GET.get('program_id')
    course_id = request.GET.get('course_id')
    project_id = request.GET.get('project_id')

    data = {
        'saved_dashboard_filters': [],  # TODO: fetch saved filters
        'programs': get_accessible_programs(request.user, restrict_to_programs_ids),
        'restrict_to_users': restrict_to_users_ids,
        'selected_program_id': program_id if program_id else "",
        'selected_course_id': course_id if course_id else "",
        'selected_project_id': project_id if project_id else "",
        "remote_session_key": request.session.get("remote_session_key"),
        "lms_base_domain": settings.LMS_BASE_DOMAIN,
        "lms_sub_domain": settings.LMS_SUB_DOMAIN,
        "use_current_host": getattr(settings, 'IS_EDXAPP_ON_SAME_DOMAIN', True),
    }

    return render(request, template, data)

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_TA)
@checked_program_access  # note this decorator changes method signature by adding restrict_to_programs_ids parameter
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def groupwork_dashboard_courses(request, program_id, restrict_to_programs_ids=None, restrict_to_courses_ids=None):
    try:
        program_id = int(program_id)
    except (ValueError, TypeError):
        return make_json_error(_("Invalid program_id specified: {}").format(program_id), 400)

    user_api.set_user_preferences(request.user.id, {"DASHBOARD_PROGRAM_ID": str(program_id)})

    AccessChecker.check_has_program_access(program_id, restrict_to_programs_ids)
    accessible_courses = get_accessible_courses_from_program(request.user, int(program_id), restrict_to_courses_ids)

    data = map(lambda item: {'value': item.course_id, 'display_name': item.display_name}, accessible_courses)
    return HttpResponse(json.dumps(data), content_type="application/json")

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_TA)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def groupwork_dashboard_projects(request, course_id, restrict_to_courses_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)
    course = load_course(course_id)
    group_projects = [gp for gp in course.group_projects if gp.is_v2]  # only GPv2 support dashboard

    data = map(lambda item: {'value': item.id, 'display_name': item.name}, group_projects)
    return HttpResponse(json.dumps(data), content_type="application/json")

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_TA)
@checked_program_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def groupwork_dashboard_details(
        request, program_id, course_id, project_id, restrict_to_programs_ids=None, restrict_to_courses_ids=None
):
    try:
        program_id = int(program_id)
    except (ValueError, TypeError):
        return make_json_error(_("Invalid program_id specified: {}").format(program_id), 400)

    AccessChecker.check_has_program_access(program_id, restrict_to_programs_ids)
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)

    program = Program.fetch(program_id)
    course = load_course(course_id)
    projects = [gp for gp in course.group_projects if gp.is_v2 and gp.id == project_id]
    if not projects:
        raise Http404()

    project = projects[0]
    return_url_query_params = {'program_id': program.id, 'course_id': course.id, 'project_id': project.id}
    return_url = reverse('groupwork_dashboard') + "?" + urlencode(return_url_query_params)

    template = 'admin/workgroup/dashboard_details.haml'

    data = {
        'remote_session_key': request.session.get('remote_session_key'),
        'lms_base_domain': settings.LMS_BASE_DOMAIN,
        'lms_sub_domain': settings.LMS_SUB_DOMAIN,
        'program': {'id': program.id, 'name': '{} ({})'.format(program.display_name, program.name)},
        'course': {'id': course.id, 'name': course.name},
        'project': {'id': project.id, 'name': project.name},
        'return_url': return_url,
        'use_current_host': getattr(settings, 'IS_EDXAPP_ON_SAME_DOMAIN', True),
    }

    return render(request, template, data)

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def download_group_list(request, course_id, restrict_to_courses_ids=None, restrict_to_users_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)

    course = load_course(course_id, request=request)
    students, companies = getStudentsWithCompanies(course, restrict_to_users_ids)
    group_projects = load_group_projects_info_for_course(course, companies)
    group_project_groups, students = filter_groups_and_students(group_projects, students, restrict_to_users_ids)

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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def download_group_projects_report(request, course_id, restrict_to_courses_ids=None, restrict_to_users_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)
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
        generate_workgroup_csv_report(course_id, url_prefix, restrict_to_users_ids),
        content_type='text/csv'
    )

    response['Content-Disposition'] = 'attachment; filename={}'.format(
        filename
    )

    return response

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def group_work_status(request, course_id, group_id=None, restrict_to_courses_ids=None, restrict_to_users_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)
    wcd = WorkgroupCompletionData(course_id, group_id, restrict_to_users_ids)
    data = wcd.build_report_data()
    data.update({'selected_client_tab':'group_work_status'})

    template = 'admin/workgroup/workgroup_{}report.haml'.format('detail_' if group_id else '')

    return render(
        request,
        template,
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def workgroup_detail(request, course_id, workgroup_id, restrict_to_courses_ids=None, restrict_to_users_ids=None):
    '''
    Get detailed information about the specific workgroup for this course
    '''
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)

    workgroup = WorkGroup.fetch(workgroup_id)
    additional_fields = ["avatar_url"]
    user_ids = set(u.id for u in workgroup.users)
    if restrict_to_users_ids is not None:
        user_ids &= restrict_to_users_ids
    users = user_api.get_users(ids=[str(id) for id in user_ids], fields=additional_fields)
    project = Project.fetch(workgroup.project)

    course = load_course(course_id, request=request)
    projects = [gp for gp in course.group_projects if gp.id == project.content_id and len(gp.activities) > 0]
    activities = []
    if len(projects) > 0:
        project.name = projects[0].name
        activities = projects[0].activities

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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def workgroup_course_assignments(request, course_id, restrict_to_courses_ids=None, restrict_to_users_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)
    selected_project_id = request.GET.get("project_id", None)
    course = load_course(course_id)

    students, companies = getStudentsWithCompanies(course, restrict_to_users_ids)

    if len(course.group_projects) < 1:
        return HttpResponse(json.dumps({'message': 'No group projects available for this course'}), content_type="application/json")

    group_projects = Project.fetch_projects_for_course(course.id)
    group_project_lookup = {gp.id: gp for gp in course.group_projects}

    for project in group_projects:
        if project.content_id in group_project_lookup:
            project.status = True
            project.selected = (selected_project_id == str(project.id))
            project_definition = group_project_lookup[project.content_id]
            project.name = project_definition.name
            # Needs to be a separate copy here because we'd like to distinguish when 2 projects are both using the same activities below
            project.activities = copy.deepcopy(project_definition.activities)
        else:
            project.status = False
            project.activities = []
            project.name = project.content_id

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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def workgroup_course_detail(request, course_id, restrict_to_courses_ids=None, restrict_to_users_ids=None):
    ''' handles requests for login form and their submission '''
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)

    selected_project_id = request.GET.get("project_id", None)
    course = load_course(course_id, request=request)

    students, companies = getStudentsWithCompanies(course, restrict_to_users_ids)

    if len(course.group_projects) < 1:
        return HttpResponse(json.dumps({'message': 'No group projects available for this course'}), content_type="application/json")

    group_projects = load_group_projects_info_for_course(course, companies)
    group_project_groups, students = filter_groups_and_students(group_projects, students, restrict_to_users_ids)

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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_program_access  # note this decorator changes method signature by adding restrict_to_programs_ids parameter
def workgroup_programs_list(request, restrict_to_programs_ids=None):
    ''' handles requests for login form and their submission '''

    if request.method == 'POST':
        program_id = request.POST["group_id"]
    if request.method == 'GET':
        program_id = request.GET["group_id"]

    if program_id == 'select':
        return render(
            request,
            'admin/workgroup/courses_list.haml',
            {
                "courses": {},
            }
        )
    else:
        AccessChecker.check_has_program_access(int(program_id), restrict_to_programs_ids)
        courses = get_accessible_courses_from_program(request.user, int(program_id))

        data = {
            "courses": courses,
        }

    return render(
        request,
        'admin/workgroup/courses_list.haml',
        data
    )


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def workgroup_group_update(request, group_id, course_id, restrict_to_courses_ids=None, restrict_to_users_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)

    if request.method == 'POST':

        students = set(int(user_id) for user_id in request.POST.getlist('students[]'))
        if restrict_to_users_ids is not None:
            students &= restrict_to_users_ids

        try:
            workgroup = WorkGroup.fetch(group_id)
            workgroup.add_user_list(students)
            return HttpResponse(json.dumps({'status': 'success'}), content_type="application/json")

        except ApiError as err:
            error = err.message
            return HttpResponse(json.dumps({'status': error}), content_type="application/json")

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def workgroup_group_create(request, course_id, restrict_to_courses_ids=None, restrict_to_users_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)

    if request.method == 'POST':
        students = set(int(user_id) for user_id in request.POST.getlist('students[]'))
        if restrict_to_users_ids is not None:
            students &= restrict_to_users_ids
        project_id = request.POST['project_id']

        # load project, and make sure if private that all students are in the correct organization
        project = Project.fetch(project_id)
        if project.organization is not None:
            organization = Organization.fetch(project.organization)
            bad_users = [u for u in students if u not in organization.users]

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

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
def workgroup_group_remove(request, group_id, restrict_to_courses_ids=None, restrict_to_users_ids=None):
    if request.method == 'POST':

        remove_student = request.POST['student']
        AccessChecker.check_has_user_access(int(remove_student), restrict_to_users_ids)

        workgroup = WorkGroup.fetch(group_id)
        workgroup.remove_user(remove_student)

        course_id = request.POST['course_id']
        course = load_course(course_id, request=request)

        students, companies = getStudentsWithCompanies(course, restrict_to_users_ids)

        group_projects = load_group_projects_info_for_course(course, companies)
        group_project_groups, students = filter_groups_and_students(group_projects, students, restrict_to_users_ids)

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

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def workgroup_project_create(request, course_id, restrict_to_courses_ids=None):
    message = _("Error creating project")
    status_code = 400

    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)

    if request.method == "POST":
        project_section = request.POST["project_section"]
        organization = None
        private_project = request.POST.get("new-project-private", None)
        if private_project == "on":
            organization = request.POST["new-project-company"]

        existing_projects = Project.fetch_projects_for_course(course_id)
        matching_projects = [p for p in existing_projects if p.content_id == project_section and p.organization == organization]

        if len(matching_projects) > 0:
            message = _("Project already exists")
            status_code = 409 # 409 = conflict
        else:
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
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def workgroup_remove_project(request, project_id, restrict_to_courses_ids=None):
    project = Project.fetch(project_id)
    AccessChecker.check_has_course_access(project.course_id, restrict_to_courses_ids)

    try:
        Project.delete(project_id)
    except ApiError as e:
        message = e.message
        status_code = e.code
        response = HttpResponse(json.dumps({"message": message}), content_type="application/json")
        response.status_code = status_code
        return response

    return HttpResponse(json.dumps({"message": "Project deleted successfully."}), content_type="application/json")

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_program_access  # note this decorator changes method signature by adding restrict_to_programs_ids parameter
def workgroup_list(request, restrict_to_programs_ids=None):
    ''' handles requests for login form and their submission '''

    if request.method == 'POST':
        if request.POST['select-program'] != 'select' and request.POST['select-course'] != 'select':
            return HttpResponseRedirect('/admin/workgroup/course/{}'.format(request.POST['select-course']))

    programs = get_accessible_programs(request.user, restrict_to_programs_ids)

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


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@checked_user_access  # note this decorator changes method signature by adding restrict_to_users_ids parameter
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def edit_permissions(request, user_id, restrict_to_users_ids=None, restrict_to_courses_ids=None):
    '''
    define or edit existing roles for a single user
    '''
    user = user_api.get_user(user_id)
    error = None

    if request.user.is_mcka_admin:
        form_class = AdminPermissionForm
    else:
        form_class = BasePermissionForm
        AccessChecker.check_has_user_access(int(user_id), restrict_to_users_ids)

    permissions = Permissions(user_id)
    courses = permissions.courses
    if restrict_to_courses_ids is not None:
        courses = [course for course in courses if course.id in restrict_to_courses_ids]

    if request.method == 'POST':
        form = form_class(courses, request.POST)
        if form.is_valid():
            per_course_roles = []
            for course in courses:
                course_roles = form.cleaned_data.get(course.id, [])
                for role in course_roles:
                    per_course_roles.append({
                        'course_id': course.id,
                        'role': role
                    })
            # Include the current settings for courses which the user doesn't have the right to modify.
            for course in permissions.courses:
                if course not in courses:
                    extension = [
                        {'course_id': course.id, 'role': role.role}
                        for role in permissions.user_roles if role.course_id == course.id
                    ]
                    per_course_roles.extend(extension)

            if request.user.is_mcka_admin:
                new_perms = form.cleaned_data.get('permissions')
            else:
                # TA and observer are not handled through this list when saving it-- they're calculated
                # through the course roles.
                # Also, this needs to be a distinct copy, lest we edit the list while using it, so a new
                # list is created.
                new_perms = [
                    perm for perm in permissions.current_permissions
                    if perm not in (PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.MCKA_OBSERVER)
                ]
            try:
                permissions.save(new_perms, per_course_roles)
            except PermissionSaveError as err:
                error = str(err)
            else:
                return HttpResponseRedirect('/admin/permissions')
    else:
        initial_data = {
            'permissions': permissions.current_permissions
        }

        for course in courses:
            initial_data[course.id] = []
            for role in permissions.user_roles:
                if course.id == role.course_id:
                    initial_data[course.id].append(role.role)

        form = form_class(courses, initial=initial_data, label_suffix='')

    data = {
        'form': form,
        'error': error,
        'user': user,
        'submit_label': _("Save")
    }
    return render(request, 'admin/permissions/edit.haml', data)

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def permissions(request):
    '''
    For McKinsey Admins, show users within "Administrative" company, and also users that have no company association.

    For Internal Admins, show users within their company.
    '''
    organizations = Organization.list()
    ADMINISTRATIVE = 0

    if request.user.is_mcka_admin:
        organization_options = [(ADMINISTRATIVE, 'ADMINISTRATIVE')]
        organization_options.extend(
            [(org.id, org.display_name) for org in organizations if org.name != settings.ADMINISTRATIVE_COMPANY]
        )
        org_id = int(request.GET.get('organization', ADMINISTRATIVE))
        users = get_admin_users(organizations, org_id, ADMINISTRATIVE)
    else:
        org = AccessChecker.get_organization_for_user(request.user)
        if not org:
            return permission_denied(request)
        organization_options = None
        org_id = org.id
        users = get_admin_users(organizations, org_id, ADMINISTRATIVE)

    # get the groups and for each group get the list of users, then intersect them appropriately
    groups = group_api.get_groups_of_type(group_api.PERMISSION_TYPE)
    group_members = {group.name : [gu.id for gu in group_api.get_users_in_group(group.id)] for group in groups}

    _role_map = {
        PERMISSION_GROUPS.MCKA_TA: _('TA'),
        PERMISSION_GROUPS.MCKA_OBSERVER: _('OBSERVER'),
        PERMISSION_GROUPS.MCKA_ADMIN: _('ADMIN'),
        PERMISSION_GROUPS.CLIENT_ADMIN: _('COMPANY ADMIN'),
        PERMISSION_GROUPS.INTERNAL_ADMIN: _('INTERNAL ADMIN'),
    }

    for user in users:
        roles = [
            role_name
            for role_key, role_name in _role_map.iteritems()
            if user.id in group_members.get(role_key, [])
        ]
        user.roles = ", ".join(roles)
        user.company_list = ", ".join([org.display_name for org in user.organizations])

    data = {
        'users': users,
        'organization_options': organization_options,
        'organization_id': org_id
    }
    return render(request, 'admin/permissions/list.haml', data)

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.INTERNAL_ADMIN)
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
