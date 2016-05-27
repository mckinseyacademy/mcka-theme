import copy
import functools
import json
import string
import urlparse
import re
from dateutil.parser import parse as parsedate
from datetime import datetime
from urllib import quote as urlquote, urlencode
from operator import attrgetter
from smtplib import SMTPException

import operator
import re
import os.path
from django.conf import settings
from django.core.mail import EmailMessage, send_mass_mail
from django.core import serializers
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import render, redirect
from django.template import loader, RequestContext
from django.utils.dateformat import format
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.views.generic.base import View

from admin.controller import get_accessible_programs, get_accessible_courses_from_program, \
    load_group_projects_info_for_course
from api_client.group_api import PERMISSION_GROUPS
from api_client.user_api import USER_ROLES
from lib.authorization import permission_group_required, permission_group_required_api
from lib.mail import sendMultipleEmails, email_add_active_student, email_add_inactive_student
from accounts.models import UserActivation
from accounts.controller import is_future_start, save_new_client_image, send_password_reset_email
from api_client import user_models
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
    AccessKey, DashboardAdminQuickFilter, BatchOperationStatus, BatchOperationErrors, BrandingSettings, 
    LearnerDashboard, LearnerDashboardDiscovery, LearnerDashboardTile, EmailTemplate, CompanyInvoicingDetails, CompanyContact
)
from .controller import (
    get_student_list_as_file, get_group_list_as_file, fetch_clients_with_program, load_course,
    getStudentsWithCompanies, filter_groups_and_students, get_group_activity_xblock,
    upload_student_list_threaded, mass_student_enroll_threaded, generate_course_report, get_organizations_users_completion,
    get_course_analytics_progress_data, get_contacts_for_client, get_admin_users, get_program_data_for_report,
    MINIMAL_COURSE_DEPTH, generate_access_key, serialize_quick_link, get_course_details_progress_data, 
    get_course_engagement_summary, get_course_social_engagement, course_bulk_actions, get_course_users_roles, 
    get_user_courses_helper, get_course_progress, import_participants_threaded, change_user_status, unenroll_participant,
    _send_activation_email_to_single_new_user, _send_multiple_emails, send_activation_emails_by_task_key
)
from .forms import (
    ClientForm, ProgramForm, UploadStudentListForm, ProgramAssociationForm, CuratedContentItemForm,
    AdminPermissionForm, BasePermissionForm, UploadCompanyImageForm,
    EditEmailForm, ShareAccessKeyForm, CreateAccessKeyForm, MassStudentListForm, EditExistingUserForm,
    DashboardAdminQuickFilterForm, BrandingSettingsForm, DiscoveryContentCreateForm, LearnerDashboardTileForm, 
    CreateNewParticipant
)
from .review_assignments import ReviewAssignmentProcessor, ReviewAssignmentUnattainableError
from .workgroup_reports import generate_workgroup_csv_report, WorkgroupCompletionData
from .permissions import Permissions, PermissionSaveError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from courses.user_courses import load_course_progress
import csv


# TO-DO: DECORATOR TO CHECK LEARNER DASHBOARD FEATURE IS ON. 
# ADD TO LD VIEWS ONCE TESTING IS COMPLETE.
def check_learner_dashboard_flag(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        obj = func(*args, **kwargs)
        request = args[0]
        if settings.LEARNER_DASHBOARD_ENABLED is False:
            return render(request, '403.haml')
        else:
            return obj

    return wrapper

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
    def get_clients_user_has_access_to(user):
        if user.is_mcka_admin:
            return Client.list()
        return user_api.get_user_organizations(user.id, organization_object=Client)

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
        'cutoffs': cutoffs,
        'learner_dashboard_enabled': settings.LEARNER_DASHBOARD_ENABLED,
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
        'students': students,
        'learner_dashboard_enabled': settings.LEARNER_DASHBOARD_ENABLED,
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
        'learner_dashboard_enabled': settings.LEARNER_DASHBOARD_ENABLED,
    }
    return render(
        request,
        'admin/client-admin/course_analytics.haml',
        data,
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
@client_admin_access
def client_admin_course_learner_dashboard(request, client_id, course_id):

    try:
        instance = LearnerDashboard.objects.get(client_id=client_id, course_id=course_id)
    except:
        instance = None

    if request.method == "POST":
        if instance == None:
            instance = LearnerDashboard(
                title = request.POST['title'],
                description = request.POST['description'],
                title_color = request.POST['title_color'],
                description_color = request.POST['description_color'],
                client_id = client_id, 
                course_id = course_id
            )
            instance.save()
        else:
            instance.title = request.POST['title']
            instance.description = request.POST['description']
            instance.title_color = request.POST['title_color']
            instance.description_color = request.POST['description_color']
            instance.save()
        
            myDict = dict(request.POST.iterlists())
            for index, item_id in enumerate(myDict['positions[]']):
                tileItem = LearnerDashboardTile.objects.get(id=item_id)
                tileItem.position = index
                tileItem.save()

    if instance:
        try:
            branding = BrandingSettings.objects.get(client_id=client_id)
        except:
            branding = None

        discovery_items = LearnerDashboardDiscovery.objects.filter(learner_dashboard=instance.id).order_by('position')
        learner_dashboard_tiles = LearnerDashboardTile.objects.filter(learner_dashboard=instance.id).order_by('position')
        
        data = {
            'client_id': client_id,
            'course_id': course_id,
            'learner_dashboard_id': instance.id,
            'title': instance.title,
            'description': instance.description,
            'title_color': instance.title_color,
            'description_color': instance.description_color,
            'learner_dashboard_tiles': learner_dashboard_tiles,
            'learner_dashboard_enabled': settings.LEARNER_DASHBOARD_ENABLED,
            'discovery_items': discovery_items,
            'branding': branding
        }
    else:
        data = {
            'client_id': client_id,
            'course_id': course_id,
            'learner_dashboard_id': None,
            'learner_dashboard_enabled': settings.LEARNER_DASHBOARD_ENABLED,
        }

    return render(request, 'admin/client-admin/learner_dashboard.haml', data)

@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.CLIENT_ADMIN)
def client_admin_course_learner_dashboard_tile(request, client_id, course_id, learner_dashboard_id, tile_id):

    error = None
    try:
        instance = LearnerDashboardTile.objects.get(id=tile_id)
    except:
        instance = None

    if request.method == 'POST':
        form = LearnerDashboardTileForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            tile = form.save()

            if not "/learnerdashboard/" in tile.link:
                if tile.get_tile_type_display() == 'Lesson':
                    tile.link = "/learnerdashboard" + tile.link + "/lesson"
                if tile.get_tile_type_display() == 'Module':
                    tile.link = "/learnerdashboard" + tile.link + "/module/"
                tile.save()
            if tile.get_tile_type_display() == 'Course':
                if not "/courses/" in tile.link:
                    tile.link = "/courses/" + tile.link
                    tile.save()

            redirect_url = reverse('client_admin_course_learner_dashboard', kwargs={'client_id': client_id, 'course_id': course_id})
            return HttpResponseRedirect(redirect_url)
    elif request.method == 'DELETE':
        instance.delete()
        redirect_url = reverse('client_admin_course_learner_dashboard', kwargs={'client_id': client_id, 'course_id': course_id})
        return HttpResponseRedirect(redirect_url)
    else:
        form = LearnerDashboardTileForm(instance=instance)

    default_colors = {
        'label': settings.TILE_LABEL_COLOR,
        'note': settings.TILE_NOTE_COLOR,
        'title': settings.TILE_TITLE_COLOR,
        'background': settings.TILE_BACKGROUND_COLOR,
    }

    return render(request, 'admin/client-admin/learner_dashboard_tile_modal.haml', {
        'error': error,
        'form': form,
        'client_id': client_id,
        'course_id': course_id,
        'learner_dashboard_id': learner_dashboard_id,
        'tile_id': tile_id,
        'default_colors': default_colors,
    })


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

class participant_details_courses_unenroll_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, user_id, course_id, format=None):
        
        try:
            # TO-DO: Change with actual enroll once provided by EDX. 
            # Sets to Observer for now.
            response = unenroll_participant(course_id, user_id)
            return HttpResponse(
                    json.dumps(response),
                    content_type='application/json'
                )
        except ApiError as err:
            error = err.message
            return HttpResponseServerError(
                {'status': 'error', 'message': error}, 
                content_type='application/json'
            )

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
def courses_list(request):
    return render(request, 'admin/courses/courses_list.haml')


class courses_list_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, format=None):
        allCourses = course_api.get_courses_list(request.GET)
        for course in allCourses:
            if course['start'] is not None:
                start = parsedate(course['start'])
                course['start'] = start.strftime("%Y/%m/%d") + ',' + start.strftime("%m/%d/%Y")
            if course['end'] is not None:
                end = parsedate(course['end'])
                course['end'] = end.strftime("%Y/%m/%d")  + ',' + end.strftime("%m/%d/%Y")
            for data in course:
                if course.get(data) is None:
                    course[data] = "-"        
        return Response(allCourses)


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def course_details(request, course_id):

    course = course_api.get_course_details(course_id)
    course_metrics_end = datetime.now().strftime("%m/%d/%Y")
    if course['start'] is not None:
        course['start'] = parsedate(course['start']).strftime("%m/%d/%Y")
    if course['end'] is not None:
        course['end'] = parsedate(course['end']).strftime("%m/%d/%Y") 
        course_metrics_end = course['end'] 
    for data in course:
        if course.get(data) is None:
            course[data] = "-"  

    course_all_users = course_api.get_course_details_users(course_id)
    count = len(course_all_users['enrollments'])
    users_enrolled = []
    permissionsFilter = ['observer','assistant', 'staff', 'instructor']
    list_of_user_roles = get_course_users_roles(course_id, permissionsFilter)
    for user in course_all_users['enrollments']:
        if str(user['id']) not in list_of_user_roles['ids']:
            users_enrolled.append(user)

    course['users_enrolled'] = len(users_enrolled)

    course_completed_users = 0
    course_metrics = course_api.get_course_time_series_metrics(course_id, course['start'], course['end'], interval='months')
    for completed_metric in course_metrics.users_completed:
        course_completed_users += completed_metric[1]
    try:
        course['completed'] = round_to_int_bump_zero(100 * course_completed_users / len(users_enrolled))
    except ZeroDivisionError:
        course['completed'] = 0

    course_pass = course_api.get_course_metrics_grades(course_id, grade_object_type=Proficiency, count=course['users_enrolled'])
    course['passed'] = course_pass.pass_rate_display(users_enrolled)

    course_progress = 0
    course_proficiency = 0

    users_progress = get_course_progress(course_id, users_enrolled, request)

    for user in users_progress:
        course_progress += user['progress']

    course_grades = course_api.get_course_details_metrics_grades(course_id, count)
    for user in course_grades['leaders']:
        if any(item['id'] == user['id'] for item in users_enrolled):
            user_proficiency = float(user['grade'])*100
            course_proficiency += user_proficiency

    try:
        course['average_progress'] = round_to_int_bump_zero(float(course_progress)/course['users_enrolled'])
    except ZeroDivisionError:
        course['average_progress'] = 0
    try:
        course['proficiency'] = round_to_int_bump_zero(float(course_proficiency)/course['users_enrolled'])
    except ZeroDivisionError:
        course['proficiency'] = 0

    list_of_email_templates = EmailTemplate.objects.all()
    course['template_list'] = []
    for email_template in list_of_email_templates:    
        course['template_list'].append({'pk':email_template.pk, 'title':email_template.title})

    return render(request, 'admin/courses/course_details.haml', course)

class course_details_stats_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, course_id, format=None):
        
        course_stats = get_course_social_engagement(course_id)
        return Response(course_stats)


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def download_course_stats(request, course_id):

    course = course_api.get_course_details(course_id)
    course_name = course['name'].replace(' ', '_')

    course_social_engagement = get_course_social_engagement(course_id)
    course_engagement_summary = get_course_engagement_summary(course_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + course_name + '_stats.csv"'

    writer = csv.writer(response)
    writer.writerow(['Engagement Summary', '# of people', '% total cohort', 'Avg Progress'])
    for stat in course_engagement_summary:
        writer.writerow([stat['name'], stat['people'], stat['invited'], stat['progress']])
    writer.writerow([])
    writer.writerow(['Participant Performance', '% completion', 'Score'])
    writer.writerow(['Group work 1', '-', '-'])
    writer.writerow(['Group work 2', '-', '-'])
    writer.writerow(['Mid-course assessment', '-', '-'])
    writer.writerow(['Final assessment', '-', '-'])
    writer.writerow([])
    writer.writerow(['Social Engagement', '#'])
    for stat in course_social_engagement:
        writer.writerow([stat['name'], stat['value']])
    
    return response


class course_details_engagement_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, course_id, format=None):
        
        course_stats = get_course_engagement_summary(course_id)
        
        return Response(course_stats)


class course_details_cohort_timeline_api(APIView):
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, course_id):
        course = load_course(course_id)
        course_modules = course.components_ids(settings.PROGRESS_IGNORE_COMPONENTS)

        users = course_api.get_user_list(course.id)

        metricsJson = get_course_details_progress_data(course, course_modules, users)

        jsonResult = [{"key": "% Progress", "values": metricsJson[0]},
                        {"key": "% Progress (Engaged)", "values": metricsJson[1]}]
        return HttpResponse(
                    json.dumps(jsonResult),
                    content_type='application/json'
                )


class course_details_performance_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, course_id, format=None):
        
        course_users_simple = course_api.get_user_list(course_id)
        course_users_ids = [str(user.id) for user in course_users_simple]
        roles = course_api.get_users_filtered_by_role(course_id)
        roles_ids = [str(user.id) for user in roles]
        for role_id in roles_ids:
            if role_id in course_users_ids: course_users_ids.remove(role_id)

        additional_fields = ["is_active"]
        course_users = user_api.get_users(ids=course_users_ids, fields=additional_fields)
        course_metrics = course_api.get_course_metrics_completions(course_id, count=len(course_users_simple))
        course_progress = course_metrics.course_avg
        course_leaders_ids = [leader.id for leader in course_metrics.leaders]

        active_users = 0
        engaged_users = 0
        engaged_progress_sum = sum([leader.completions for leader in course_metrics.leaders])
        for course_user in course_users:
            if course_user.is_active is True:
                active_users += 1
            if course_user.id in course_leaders_ids:
                engaged_users += 1

        activated = round_to_int(active_users/len(course_users)) if len(course_users) > 0 else 0
        engaged = round_to_int(engaged_users/len(course_users)) if len(course_users) > 0 else 0
        active_progress = round_to_int(engaged_progress_sum/active_users) if active_users > 0 else 0
        engaged_progress = round_to_int(engaged_progress_sum/engaged_users) if engaged_users > 0 else 0

        course_stats = [
             { 'name': 'Total Cohort', 'people': len(course_users), 'invited': '-', 'progress': course_progress},
             { 'name': 'Activated', 'people': active_users, 'invited': str(activated * 100) + '%', 'progress': str(active_progress) + '%'},
             { 'name': 'Engaged', 'people': engaged_users, 'invited': str(engaged * 100) + '%', 'progress': str(engaged_progress) + '%'},
             { 'name': 'Logged in over last 7 days', 'people': 'N/A', 'invited': 'N/A', 'progress': 'N/A'}
        ]
        return Response(course_stats)

class course_details_api(APIView):
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, course_id=None, format=None):
        if (course_id):
            permissonsMap = {
            'assistant':'TA',
            'instructor': 'Instructor',
            'staff':'Staff',
            'observer':'Observer'
            }
            permissionsFilter = ['observer','assistant']
            allCoursesParticipantList = []
            len_of_all_users = 0
            userData = {'ids':[]}
            current_page = 0
            if request.GET.get('include_slow_fields', 'false') == 'true':
                allCourseParticipantsUsers = user_api.get_filtered_users(request.GET)
                users_progress = get_course_progress(course_id, allCourseParticipantsUsers['results'], request)
                len_of_all_users = len(allCourseParticipantsUsers['results'])
                allCourseParticipants = allCourseParticipantsUsers['results']
            else:
                allCourseParticipants = course_api.get_user_list_dictionary(course_id)['enrollments']
                list_of_user_roles = get_course_users_roles(course_id, permissionsFilter)
                allCourseParticipants = sorted(allCourseParticipants, key=lambda k: k['id'])
                for user_role_id in list_of_user_roles['ids']:          
                    userData['ids'].append(str(user_role_id))
                for course_participant in allCourseParticipants:
                    if str(course_participant['id']) not in userData['ids']:
                        userData['ids'].append(str(course_participant['id']))
                requestParams = dict(request.GET)
                if requestParams['page_size']:
                    len_of_pages = int(requestParams['page_size'][0])
                else:
                    len_of_pages = 50;
                user_chunked_ids=[userData['ids'][x:x+len_of_pages] for x in xrange(0, len(userData['ids']), len_of_pages)]
                len_of_all_users = len(userData['ids'])
                if requestParams['page']:
                    if int(requestParams['page'][0]) > 0:
                        current_page = int(requestParams['page'][0])-1
                    else:
                        current_page = 0
                else:
                    current_page = 0;
                del requestParams['include_slow_fields']       
                userData['ids'] = ",".join(user_chunked_ids[current_page])
                for key, value in requestParams.items():
                    requestParams[key] = ",".join(value)
                requestParams.update(userData)
                requestParams['page'] = 1
                allCourseParticipantsUsers = user_api.get_filtered_users(requestParams)

                course_all_users = course_api.get_course_details_users(course_id)
                count = len(course_all_users['enrollments'])
                course_grades = course_api.get_course_details_metrics_grades(course_id, count)

            allCourseParticipantsUsers['full_length'] = len_of_all_users
            allCourseParticipantsUsers['current_page'] = current_page+1
            
            number_of_assessments = 0
            number_of_groupworks = 0
            test_groupwork = []
            test_assessment = []
            if len_of_all_users > 0:
                user_grades = user_api.get_user_full_gradebook(allCourseParticipants[0]['id'], course_id)['grade_summary']['section_breakdown']
                for user_grade in user_grades:
                    data = user_grade
                    data['percent'] = '.'
                    if 'assessment' in user_grade['category'].lower():
                        number_of_assessments += 1
                        test_assessment.append(data)
                    if 'GROUP_PROJECT' in user_grade['category']:
                        number_of_groupworks += 1
                        test_groupwork.append(data)
            for course_participant in allCourseParticipantsUsers['results']:
                if request.GET.get('include_slow_fields', 'false') == 'true':  
                    course_participant['progress'] = '{:03d}'.format(round_to_int([user['progress'] for user in users_progress if user['user_id'] == course_participant['id']][0]))
                    user_grades = user_api.get_user_full_gradebook(course_participant['id'], course_id)['grade_summary']['section_breakdown']
                    course_participant['groupworks'] = []
                    course_participant['assessments'] = []
                    for user_grade in user_grades:
                        data = user_grade
                        data['percent'] = '{:03d}'.format(round_to_int(float(user_grade['percent'])*100))
                        if 'GROUP_PROJECT' in user_grade['category']:
                            course_participant['groupworks'].append(data)
                        elif 'assessment' in user_grade['category'].lower():
                            course_participant['assessments'].append(data)
                else:
                    course_participant['user_status'] = []
                    course_participant['number_of_assessments'] = number_of_assessments
                    course_participant['number_of_groupworks'] = number_of_groupworks
                    course_participant['progress'] = '.'
                    course_participant['groupworks'] = test_groupwork
                    course_participant['assessments'] = test_assessment
                    course_participant['proficiency'] = [float(user['grade'])*100 for user in course_grades['leaders'] if user['id'] == course_participant['id']]
                    if not course_participant['proficiency']:
                        course_participant['proficiency'] = "000";
                    else:
                        course_participant['proficiency'] = '{:03d}'.format(round_to_int(course_participant['proficiency'][0]))
                    for role in list_of_user_roles['data']:
                        if role['id'] == course_participant['id']:
                            course_participant['user_status'].append(permissonsMap[role['role']])
                            del role['role']
                    if permissonsMap['assistant'] in course_participant['user_status']:
                        course_participant['custom_user_status'] = 'TA'
                    elif permissonsMap['observer'] in course_participant['user_status']:
                        course_participant['custom_user_status'] = 'Observer'
                    else:
                        course_participant['custom_user_status']='Active'
                        course_participant['user_status'].append('Active')
                    course_participant['progress'] = '.'
                    if len(course_participant['organizations'] ) == 0:
                        course_participant['organizations'] = [{'display_name': 'No company'}]
                        course_participant['organizations_display_name'] = 'No company'
                    else:
                        course_participant['organizations_display_name'] = course_participant['organizations'][0]['display_name']
                    if course_participant['is_active']:
                        course_participant['custom_activated'] = 'Yes'
                    else:
                        course_participant['custom_activated'] = 'No'
                    if 'last_login' in course_participant:
                        if (course_participant['last_login'] is not None) and (course_participant['last_login'] is not ''):
                            course_participant['custom_last_login'] = parsedate(course_participant['last_login']).strftime("%Y/%m/%d")
                        else:
                            course_participant['custom_last_login'] = '-'
                    else:
                        course_participant['custom_last_login'] = '-'
                    if 'created' in course_participant:
                        if (course_participant['created'] is not None) and (course_participant['created'] is not ''):
                            course_participant['custom_created'] = parsedate(course_participant['created']).strftime("%Y/%m/%d")
                        else:
                            course_participant['custom_created'] = '-'
                    else:
                        course_participant['custom_created'] = '-'
            return Response(allCourseParticipantsUsers)
        else:
            return Response({})
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def post(self, request, course_id=None, format=None):
        data = json.loads(request.body)
        if (data['type'] == 'status_check'):
            batch_status = BatchOperationStatus.objects.filter(task_key=data['task_id'])      
            BatchOperationStatus.clean_old()
            if len(batch_status) > 0:
                batch_status = batch_status[0]
                error_list = []
                if batch_status.failed > 0:
                    batch_errors = BatchOperationErrors.objects.filter(task_key=data['task_id'])
                    for b_error in batch_errors:
                        error_list.append({'id': b_error.user_id, 'message': b_error.error})
                return Response({'status':'ok', 'values':{'selected': batch_status.attempted, 'successful': batch_status.succeded, 'failed': batch_status.failed}, 'error_list':error_list})
            return Response({'status':'error', 'message': 'No such task!'})
        
        else:        
            batch_status = BatchOperationStatus.create();
            task_id = batch_status.task_key
            course_bulk_actions(course_id, data, batch_status)
            return Response({'status':'ok', 'data': data, 'task_id': task_id})


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
        allowed_types = ["image/jpeg", "image/png", 'image/gif']
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from PIL import Image

        for upload in request.FILES:
            temp_image = request.FILES[upload]
            if temp_image.content_type in allowed_types:
                extension = os.path.splitext(temp_image.name)[1]
                temp_url = 'images/{}-{}-{}{}'.format(upload, client_id, datetime.now().strftime("%s"), extension)
                if default_storage.exists(temp_url):
                    default_storage.delete(temp_url)
                default_storage.save(temp_url, ContentFile(temp_image.read()))
                setattr(customization, upload, '/accounts/' + temp_url)

    customization.client_background_css = request.POST['client_background_css']
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


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def import_participants(request):

    if request.method == 'POST':  # If the form has been submitted...
        # A form bound to the POST data and FILE data
        form = MassStudentListForm(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass
            reg_status = UserRegistrationBatch.create();
            import_participants_threaded(
                request.FILES['student_list'],
                request, 
                reg_status
            )
            return HttpResponse(
                json.dumps({"task_key": _(reg_status.task_key)}),
                content_type='text/plain'
            )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def import_participants_check(request, task_key):

    if request.method == 'GET':
        reg_status = UserRegistrationBatch.objects.filter(task_key=task_key)
        UserRegistrationBatch.clean_old()
        if len(reg_status) > 0:
            reg_status = reg_status[0]
            if reg_status.attempted == (reg_status.failed + reg_status.succeded):
                errors = UserRegistrationError.objects.filter(task_key=reg_status.task_key)
                errors_as_json = serializers.serialize('json', errors)
                message = _("Successfully Added {} Participants").format(
                    reg_status.attempted - reg_status.failed
                )
                for error in errors:
                    error.delete()
                attempted = str(reg_status.attempted)
                failed = str(reg_status.failed)
                succeded = str(reg_status.succeded)
                reg_status.delete()
                emails = request.GET.get('emails', None)
                if int(failed) == 0 and emails == 'true':
                    send_activation_emails_by_task_key(request, task_key)
                return HttpResponse(
                    '{"done":"done","error":'+errors_as_json+',"message":"'+message+'","attempted":"'+attempted+'","failed":"'+failed+'","succeded":"'+succeded+'","emails":"'+emails+'"}',
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
def download_activation_links_by_task_key(request):

    task_key = request.GET.get('task_key', None)
    user_id = request.GET.get('user_id', None)
    res_type = request.GET.get('res_type', 'csv')

    file_name = "download-activation-links-output"
    company_id = 'N/A'

    if task_key:
        uri_head = request.build_absolute_uri('/accounts/activate')
        activation_records = UserActivation.get_activations_by_task_key(task_key=task_key)

    if user_id:
        uri_head = request.build_absolute_uri('/accounts/activateV2')
        user_data = user_api.get_user(user_id=user_id)
        company_id = vars(user_api.get_user_organizations(user_id)[0])['id']
        activation_records = [UserActivation.get_user_activation(user=user_data)]
    
    if res_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'

        writer = csv.writer(response)
        writer.writerow(['Email', 'First name', 'Last name', 'Company', 'Activation Link'])
        for record in activation_records:
            user = vars(record)
            activation_full = "{}/{}".format(uri_head, user['activation_key'])
            if user_id:
                user = vars(user_data)
            writer.writerow([user['email'], user['first_name'], user['last_name'], user.get('company_id', company_id), activation_full])

    if res_type is not 'csv':
        activation_records_data = []
        for record in activation_records:
            user = vars(record)
            activation_full = "{}/{}".format(uri_head, user['activation_key'])
            if user_id:
                user = vars(user_data)
            activation_records_data.append([user['email'], user['first_name'], user['last_name'], user.get('company_id', company_id), activation_full])      

            if res_type == 'json': 
                response = HttpResponse(
                    json.dumps({"records": activation_records_data}), 
                    content_type='application/json'
                )
            if res_type == 'html':
                response = render(request,
                    'admin/participants/activation_link_modal.haml',
                    {'records': activation_records_data})

    return response
    

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def mass_student_enroll(request, client_id):
    ''' handles requests for login form and their submission '''
    error = None
    if request.method == 'POST':  # If the form has been submitted...
        # A form bound to the POST data and FILE data
        form = MassStudentListForm(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass
            program_id = request.POST['select-program']
            course_id = request.POST['select-course']
            reg_status = UserRegistrationBatch.create();
            mass_student_enroll_threaded(
                request.FILES['student_list'],
                client_id,
                program_id,
                course_id,
                request, 
                reg_status
            )
            return HttpResponse(
                json.dumps({"task_key": _(reg_status.task_key)}),
                content_type='text/plain'
            )
    else:
        ''' adds a new client '''
        form = MassStudentListForm()  # An unbound form
        restrict_to_programs_ids=None
        users = organization_api.get_users_by_enrolled(organization_id=client_id)
        client = Client.fetch(client_id)
        programs = client.fetch_programs()
        data = {
            "form": form,
            "users": users,
            "client_id": client_id,
            "programs": programs, 
            "error": error,
        }

    return render(
        request,
        'admin/client/mass_student_enroll.haml',
        data
    )

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
@client_admin_access
def mass_student_enroll_check(request, client_id, task_key):
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
        'programs': get_accessible_programs(request.user, restrict_to_programs_ids),
        'restrict_to_users': restrict_to_users_ids,
        'selected_program_id': program_id if program_id else "",
        'selected_course_id': course_id if course_id else "",
        'selected_project_id': project_id if project_id else "",
        "remote_session_key": request.session.get("remote_session_key"),
        "lms_base_domain": settings.LMS_BASE_DOMAIN,
        "lms_sub_domain": settings.LMS_SUB_DOMAIN,
        "lms_port": settings.LMS_PORT,
        "use_current_host": getattr(settings, 'IS_EDXAPP_ON_SAME_DOMAIN', True),
    }

    return render(request, template, data)

class QuickLinkView(View):

    http_method_names = ['get', 'post', 'delete']

    @method_decorator(permission_group_required(
        PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_TA
    ))
    # note this decorator changes method signature by adding restrict_to_programs_ids parameter
    @method_decorator(checked_program_access)
    # note this decorator changes method signature by adding restrict_to_courses_ids parameter
    @method_decorator(checked_course_access)
    def dispatch(self, request, *args, **kwargs):
        # Args and kwargs are saved by View class **before** decorators are applied
        # so we save them (with params from decorators) once again here
        self.kwargs = kwargs
        self.args = args
        self.all_clients = set(
            client.id
            for client in AccessChecker.get_clients_user_has_access_to(request.user)
        )
        return super(QuickLinkView, self).dispatch(request, *args, **kwargs)

    def verify_link(self, link):
        """
        Verifies if user has access to given link. It returns bool rather than
        raise, as in list view we'd rather filter-out all invalid links than
        raise when e.g. Admin gets demoted we'd rather siltently filter out links
        than raise 403.

        Args:
            link: link to be verivied

        Returns: bool
        """
        restrict_to_courses_ids = self.kwargs['restrict_to_courses_ids']
        restrict_to_programs_ids = self.kwargs['restrict_to_programs_ids']
        try:
            AccessChecker.check_has_course_access(link.course_id, restrict_to_courses_ids)
            AccessChecker.check_has_program_access(link.program_id, restrict_to_programs_ids)
            if link.company_id is not None and link.company_id not in self.all_clients:
                return False
            return True
        except PermissionDenied:
            return False

    def get(self, request, *args, **kwargs):
        links = DashboardAdminQuickFilter.objects.filter(
            user_id=self.request.user.id
        )
        return HttpResponse(json.dumps([
            serialize_quick_link(link)
            for link in links
            if self.verify_link(link)
        ]), content_type="application/json")


    def post(self, request, *args, **kwargs):
        form = DashboardAdminQuickFilterForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user_id != self.request.user.id:
            raise PermissionDenied()
        self.object.delete()
        return HttpResponse(status=204)

    def form_valid(self, form):
        # Just verify user has access to all related objects
        if not self.verify_link(form.save(commit=False)):
            raise PermissionDenied()
        link, created = form.save_model_if_unique(self.request.user.id)
        if not created:
            # Saving to update date_created field
            link.save()
        return HttpResponse(json.dumps(
            serialize_quick_link(link)),
            status=201,
            content_type="application/json"
        )

    def form_invalid(self, form):
        return HttpResponse(json.dumps(form.errors), status=400)

    def get_object(self):
        try:
            return DashboardAdminQuickFilter.objects.get(
                id = self.kwargs['link_id']
            )
        except DashboardAdminQuickFilter.DoesNotExist:
            raise Http404()


def _make_select_option_response(item_id, display_name, disabled=False):
    return {'value': item_id, 'display_name': display_name, 'disabled': disabled}


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_TA)
@checked_program_access  # note this decorator changes method signature by adding restrict_to_programs_ids parameter
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def groupwork_dashboard_courses(request, program_id, restrict_to_programs_ids=None, restrict_to_courses_ids=None):
    try:
        program_id = int(program_id)
    except (ValueError, TypeError):
        return make_json_error(_("Invalid program_id specified: {}").format(program_id), 400)

    AccessChecker.check_has_program_access(program_id, restrict_to_programs_ids)

    user_api.set_user_preferences(request.user.id, {"DASHBOARD_PROGRAM_ID": str(program_id)})
    accessible_courses = get_accessible_courses_from_program(request.user, int(program_id), restrict_to_courses_ids)

    data = [_make_select_option_response(item.course_id, item.display_name) for item in accessible_courses]
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_TA)
@checked_course_access  # note this decorator changes method signature by adding restrict_to_courses_ids parameter
def groupwork_dashboard_projects(request, course_id, restrict_to_courses_ids=None):
    AccessChecker.check_has_course_access(course_id, restrict_to_courses_ids)
    course = load_course(course_id)
    group_projects = [gp for gp in course.group_projects if gp.is_v2]  # only GPv2 support dashboard

    data = [_make_select_option_response(item.id, item.name) for item in group_projects]
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_TA)
@checked_program_access  # note this decorator changes method signature by adding restrict_to_programs_ids parameter
def groupwork_dashboard_companies(request, restrict_to_programs_ids=None):
    program_id = request.GET.get('program_id')
    if program_id:
        try:
            program_id = int(program_id)
        except (ValueError, TypeError):
            return make_json_error(_("Invalid program_id specified: {}").format(program_id), 400)
        AccessChecker.check_has_program_access(program_id, restrict_to_programs_ids)

    all_clients = sorted(
        AccessChecker.get_clients_user_has_access_to(request.user),
        key=operator.attrgetter('display_name')
    )

    accessible_clients = set(
        client.id for client in all_clients
        # all clients if program_id is not specified; otherwise only clients associated with that program
        if not program_id or program_id in client.groups
    )

    data = [
        _make_select_option_response(item.id, item.display_name, item.id not in accessible_clients) for item in all_clients
    ]
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
        "lms_port": settings.LMS_PORT,
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

        if not project_id:
            return HttpResponse(
                json.dumps({'success': False, 'message': "Group wasn't created - please select project"}),
                content_type="application/json"
            )

        # load project, and make sure if private that all students are in the correct organization
        project = Project.fetch(project_id)
        if project.organization is not None:
            organization = Organization.fetch(project.organization)
            bad_users = [u for u in students if u not in organization.users]

            if len(bad_users) > 0:
                message = "Bad users {} for private project".format(",".join([u for u in bad_users]))
                return HttpResponse(json.dumps({'success': False, 'message': message}), content_type="application/json")

        workgroups = sorted(project.workgroups)
        lastId = 0 if not workgroups else int(workgroup_api.get_workgroup(workgroups[-1]).name.split()[-1])

        workgroup = WorkGroup.create(
            'Group {}'.format(lastId + 1),
            {
                "project": project_id,
            }
        )

        workgroup.add_user_list(students)

        return HttpResponse(json.dumps(
            {'success': True, 'message': 'Group successfully created'}), content_type="application/json"
        )

    return HttpResponse(json.dumps(
        {'success': False, 'message': 'Group was not created'}), content_type="application/json"
    )

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


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def participants_list(request):
    form = MassStudentListForm()
    return render( request, 'admin/participants/participants_list.haml', {"form": form})

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def participant_password_reset(request, user_id):
    try: 
        user = user_api.get_user(user_id)
        send_password_reset_email(request.META.get('HTTP_HOST'), user, request.is_secure())
        messages.success(request, 'Password Reset Email successfully sent.')
    except Exception as e:
        messages.error(request, e.message)
    return HttpResponseRedirect(reverse('participants_details', args=(user_id, )))

def participant_mail_activation_link(request, user_id):

    user = user_api.get_user(user_id)
    if user:
        try:
            if not user.is_active:
                activation_record = UserActivation.get_user_activation(user)
                email_head = request.build_absolute_uri('/accounts/activateV2') #change if we want old registration form
                _send_activation_email_to_single_new_user(activation_record, user, email_head)
                messages.info(request, "Activation email sent.")
        except Exception as e:
            messages.error(request, e.message)
    return HttpResponseRedirect(reverse('participants_details', args=(user_id, )))

class participants_list_api(APIView):
    """
    List all snippets, or create a new snippet.
    """
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, format=None):

        company = request.QUERY_PARAMS.get('company', None)
        name = request.QUERY_PARAMS.get('name', None)
        email = request.QUERY_PARAMS.get('custom_email', None)

        filters = []
        if company:
            filters.append({ 'name': 'organizations_custom_name', 'value': company.lower()})
        if name:
            filters.append({ 'name': 'full_name', 'value': name.lower()})
        if email:
            filters.append({ 'name': 'email', 'value': email.lower()})

        allParticipants = user_api.get_filtered_users(request.GET)
        for participant in allParticipants["results"]:
            if len(participant["organizations"]) > 0:
                participant["organizations_custom_name"] = participant['organizations'][0]["display_name"]
            else:
                participant['organizations_custom_name'] = ""
            participant['created_custom_date'] = parsedate(participant['created']).strftime("%Y/%m/%d")
            if participant["is_active"]:
                participant["active_custom_text"]="Yes"
            else:
                participant["active_custom_text"]="No"

        if filters:
            response = {'results': []}  
            for user in allParticipants['results']:
                for item in filters:
                    item['toAppend'] = False
                    if item['value'] in (user[item['name']]).lower():
                        item['toAppend'] = True
                if all(item['toAppend'] for item in filters):
                    response['results'].append(user)
            return Response(response)

        return Response(allParticipants)

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def post(self, request):
        post_data = json.loads(request.body)
        form = CreateNewParticipant(post_data.copy())
        if form.is_valid():
            filterUsers = {}
            existing_users_length = 0
            if post_data['email']:
                filterUsers = {'email' : post_data['email']}
                existing_users = user_api.get_filtered_users(filterUsers)
                existing_users_length += int(existing_users['count'])
            if (existing_users_length > 0):
                return Response({'status':'error', 'type': 'user_exist', 'message':'User with that email already exists!'})
            else:
                data = post_data
                try:
                    if len(data['email']) > 30:
                        data['username'] = data['email'][:29]
                    else:
                        data['username'] = data['email']
                    data['username'] = re.sub(r'\W', '', data['username'])
                    data['password'] = settings.INITIAL_PASSWORD
                    data['is_active'] = False
                    user = user_api.register_user(data)
                    user_data = vars(user)
                    roles = {
                        'assistant' : USER_ROLES.TA,
                        'observer' : USER_ROLES.OBSERVER
                    }
                    permissions_groups = {
                        'uber_admin': PERMISSION_GROUPS.MCKA_ADMIN,
                        'internal_admin': PERMISSION_GROUPS.INTERNAL_ADMIN,
                        'company_admin': PERMISSION_GROUPS.CLIENT_ADMIN,
                    }
                    if data.get('new_company_name', None):
                        try:
                            new_organization = organization_api.create_organization(organization_name=data['new_company_name'].lower().replace(" ", "_"), organization_data={"display_name": data['new_company_name']})
                            data['company'] = vars(new_organization).get("id", None)
                        except ApiError, e:
                            return Response({'status':'error', 'type': 'api_error', 'message':"Couldn't create company!"})
                    if user:
                        client = Client.fetch(data['company'])
                        try:
                            if not user.is_active:
                                activation_record = UserActivation.user_activation(user)
                                if data['send_activation_email']:
                                    email_head = request.build_absolute_uri('/accounts/activateV2') #change if we want old registration form
                                    _send_activation_email_to_single_new_user(activation_record, user, email_head)
                            client.add_user(user.id)
                        except ApiError, e:
                            return Response({'status':'error', 'type': 'api_error', 'message':"Couldn't add user to company!"})
                    courses_permissions_list = []
                    for course_permission in data['course_permissions_list']:
                        try:
                            user_api.enroll_user_in_course(user_data['id'], course_permission['course_id'])
                        except ApiError as e:
                            # Ignore 409 errors, because they indicate a user already added
                            if e.code != 409:
                                return Response({'status':'error', 'type': 'api_error', 'message':e.message})
                        if course_permission['role'] != 'active':
                            course_permission['role'] = roles[course_permission['role']]
                            courses_permissions_list.append(course_permission)
                    if len(courses_permissions_list) > 0 or data['company_permissions'] != 'none':
                        permissions = Permissions(user_data['id'])
                    if len(courses_permissions_list) > 0:
                        permissions.update_courses_roles_list(courses_permissions_list)
                    if data['company_permissions'] != 'none':
                        if data['company_permissions'] in permissions_groups:
                            permissions.add_permission(permissions_groups[data['company_permissions']])
                except ApiError, e:
                    return Response({'status':'error','type': 'api_error', 'message':e.message})
                return Response({'status':'ok', 'message':'Successfully added new user!', 'user_id': user_data['id']})
        else:
            return Response({'status':'error', 'type': 'validation_failed', 'message':form.errors})

class participant_details_api(APIView):
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, user_id):
        selectedUserResponse = user_api.get_user(user_id)
        userOrganizations = user_api.get_user_organizations(user_id)
        userOrganizationsList =[]
        for organization in userOrganizations:
            userOrganizationsList.append(vars(organization))
        if selectedUserResponse is not None:
            selectedUser = selectedUserResponse.to_dict()
            if 'last_login' in selectedUser:
                if (selectedUser['last_login'] is not None) and (selectedUser['last_login'] is not ''):
                    selectedUser['custom_last_login'] = parsedate(selectedUser['last_login']).strftime('%b %d, %Y %I:%M %P')
                else:
                    selectedUser['custom_last_login'] = 'N/A'
            else:
                selectedUser['custom_last_login'] = 'N/A'
            if len(userOrganizationsList):
                selectedUser['company_name'] = userOrganizationsList[0]['display_name']
                selectedUser['company_id'] = userOrganizationsList[0]['id']
            else:
                selectedUser['company_name'] = 'No company'
                selectedUser['company_id'] = ''
            if selectedUser['gender'] == '' or selectedUser['gender'] == None:
                selectedUser['gender'] = 'N/A'
            selectedUser['city'] = selectedUser['city'].strip()
            selectedUser['country'] = selectedUser['country'].strip().upper()
            if selectedUser['city'] == '' and selectedUser['country'] == '':
                selectedUser['location'] = 'N/A'
            elif selectedUser['country'] == '':
                selectedUser['location'] = selectedUser['city']
            elif selectedUser['city'] == '':
                selectedUser['location'] = selectedUser['country']
            else:
                selectedUser['location'] = selectedUser['city'] + ', ' + selectedUser['country']
            selectedUser['mcka_permissions'] = vars(Permissions(user_id))['current_permissions']
            if not len(selectedUser['mcka_permissions']):
                selectedUser['mcka_permissions'] = ['-']
            if UserActivation.get_user_activation(user=selectedUserResponse):
                selectedUser['has_activation_record'] = True
            else:
                selectedUser['has_activation_record'] = False
            return render( request, 'admin/participants/participant_details.haml', selectedUser)

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def post(self, request, user_id, format=None):
        form = EditExistingUserForm(request.POST.copy())
        if form.is_valid():
            filterUsers = {}
            existing_users_length = 0
            if request.POST['username']:
                filterUsers = {'username' : request.POST['username']}
                existing_users = user_api.get_filtered_users(filterUsers)
                existing_users_length += int(existing_users['count'])
                for user in existing_users['results']:
                    if int(user['id']) == int(user_id):
                        existing_users_length -= 1
            if request.POST['email']:
                filterUsers = {'email' : request.POST['email']}
                existing_users = user_api.get_filtered_users(filterUsers)
                existing_users_length += int(existing_users['count'])
                for user in existing_users['results']:
                    if int(user['id']) == int(user_id):
                        existing_users_length -= 1
            if (existing_users_length > 0):
                return Response({'status':'error', 'type': 'user_exist', 'message':'User with that username or email already exists!'})
            else:
                data = form.cleaned_data
                try:
                    company = data.get('company', None)
                    company_old = request.DATA.get('company_old', None)
                    if data.get('company', None) != data.get('company_old', None):
                        organization_api.add_user_to_organization(company, user_id)
                        organization_api.remove_users_from_organization(company_old, user_id)
                    response = user_api.update_user_information(user_id,data)
                except ApiError, e:
                    return Response({'status':'error','type': 'api_error', 'message':e.message})
                return Response({'status':'ok', 'message':vars(response)})
        else:
            return Response({'status':'error', 'type': 'validation_failed', 'message':form.errors})

class manage_user_company_api(APIView):
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request):
        user_id = request.GET.get('user_id','');
        response_obj = {}
        if user_id != '':
            selectedUser = user_api.get_user(user_id)
            if selectedUser is not None:
                selectedUser = selectedUser.to_dict()
            else:
                return Response({'status':'ok', 'message':"Can't find user in database"}) 
            userOrganizations = user_api.get_user_organizations(user_id)
            userOrganizationsList =[]
            for organization in userOrganizations:
                organizationData = vars(organization)
                userOrganizationsList.append({'display_name':organizationData['display_name'], 'id': organizationData['id']})
            response_obj['user_organizations'] = userOrganizationsList
        organization_list = organization_api.get_organizations()
        allOrganizationsList =[]
        for organization in organization_list:
            organizationData = vars(organization)
            allOrganizationsList.append({'display_name':organizationData['display_name'], 'id': organizationData['id']})
        response_obj['all_items'] = allOrganizationsList
        response_obj['status'] = 'ok'
        return Response(response_obj)

class manage_user_courses_api(APIView):
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request):
        response_obj = {}
        courses_list = course_api.get_course_list()
        allCoursesList =[]
        for course in courses_list:
            courseData = vars(course)
            allCoursesList.append({'display_name':courseData['name'], 'id': courseData['id']})
        response_obj['all_items'] = allCoursesList
        response_obj['status'] = 'ok'
        return Response(response_obj)

@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def validate_participant_email(request):

    email = request.GET.get('email', None)
    userId = request.GET.get('userId', None)

    if email:
        user = user_api.get_user_by_email(email)
        if user['count'] == 0:
            return HttpResponse(json.dumps({'status': 'notTaken'}), content_type="application/json")
        elif user['count'] >=1 and user['results'][0]['email'] == email:
            if int(user['results'][0]['id']) == int(userId):
                return HttpResponse(json.dumps({'status': 'his'}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({'status': 'taken'}), content_type="application/json")


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def validate_participant_username(request):

    username = request.GET.get('username', None)
    userId = request.GET.get('userId', None)

    if username:
        user = user_api.get_user_by_username(username)
        if user['count'] == 0:
            return HttpResponse(json.dumps({'status': 'notTaken'}), content_type="application/json")
        elif user['count'] >=1 and user['results'][0]['username'] == username:
            if int(user['results'][0]['id']) == int(userId):
                return HttpResponse(json.dumps({'status': 'his'}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({'status': 'taken'}), content_type="application/json")

      
class participant_details_active_courses_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, user_id, format=None):

        include_slow_fields = request.GET.get('include_slow_fields', 'false')

        if include_slow_fields == 'false':
            active_courses, course_history = get_user_courses_helper(user_id)
            return Response(active_courses)
        elif include_slow_fields == 'true':  
            fetch_courses =[]
            for course_id in request.GET['ids'].split(','):
                user_course = {}
                user_course['id'] = course_id
                course_data = None
                course_data = load_course(user_course['id'], request=request)
                load_course_progress(course_data, user_id)
                user_course['progress'] = '{:03d}'.format(int(course_data.user_progress))
                proficiency = course_api.get_course_metrics_grades(user_course['id'], user_id=user_id, grade_object_type=Proficiency)
                user_course['proficiency'] = '{:03d}'.format(round_to_int(proficiency.user_grade_value * 100))
                fetch_courses.append(user_course)   
            return Response(fetch_courses) 

        return Response({})


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def download_active_courses_stats(request, user_id):

    active_courses, course_history = get_user_courses_helper(user_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="active_courses_stats.csv"'

    writer = csv.writer(response)
    writer.writerow(['Course', 'Course ID', 'Program', 'Progress', 'Proficiency', 'Status'])
    for course in active_courses:
        course_data = None
        course_data = load_course(course['id'], request=request)
        load_course_progress(course_data, user_id)
        course['progress'] = '{:d}%'.format(int(course_data.user_progress))
        proficiency = course_api.get_course_metrics_grades(course['id'], user_id=user_id, grade_object_type=Proficiency)
        course['proficiency'] = '{:d}%'.format(round_to_int(proficiency.user_grade_value * 100))
        writer.writerow([course['name'], course['id'], course['program'], course['progress'], course['proficiency'], course['status']])
    
    return response


class participant_details_course_edit_status_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, user_id, course_id, format=None):
        params = urlparse.parse_qs(request.GET.urlencode())
        current_roles = ''
        if params['currentRoles']:
            current_roles = str(params['currentRoles'][0])
        data = {
            'user_id': user_id, 
            'course_id': course_id, 
            'current_roles': current_roles, 
            'status': ''
        }
        return HttpResponse(render(request, 'admin/participants/participant_edit_status.haml', data))

    def post(self, request, user_id, course_id, format=None):
        new_status = request.POST.get('role-group', None)
        current_roles = request.POST.get('current-roles', '')
        change_user_status(course_id, new_status, {'id': user_id, 'existing_roles': current_roles})
        data = {'user_id': user_id, 'course_id': course_id, 'current_roles': new_status, 'status': 'Success.'}
        return HttpResponse(render(request, 'admin/participants/participant_edit_status.haml', data))


class participant_details_course_history_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, user_id, format=None):

        active_courses, course_history = get_user_courses_helper(user_id)

        user_grades = user_api.get_user_grades(user_id)

        for grade in user_grades:
            for user_course in course_history:
                if vars(grade)['course_id'] == user_course['id']:
                    if vars(grade)['complete_status'] == 'true':
                        user_course['completed'] ='Yes'
                    else:
                        user_course['completed'] = 'No'
                    user_course['grade'] = round_to_int(vars(grade)['current_grade'] * 100)
                else:
                    if user_course['status'] == 'Active':
                        user_course['completed'] = 'No'
                        user_course['grade'] = 0

                user_course['end'] = parsedate(user_course['end']).strftime("%Y/%m/%d")

        return Response(course_history) 


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def download_course_history_stats(request, user_id):

    active_courses, course_history = get_user_courses_helper(user_id)
    user_grades = user_api.get_user_grades(user_id)
    for grade in user_grades:
        for user_course in course_history:
            if vars(grade)['course_id'] == user_course['id']:
                if vars(grade)['complete_status'] == 'true':
                    user_course['completed'] ='Yes'
                else:
                    user_course['completed'] = 'No'
                user_course['grade'] = round_to_int(vars(grade)['current_grade'] * 100)
            else:
                if user_course['status'] == 'Active':
                    user_course['completed'] = 'No'
                    user_course['grade'] = 0
            user_course['end'] = parsedate(user_course['end']).strftime("%Y/%m/%d")
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="course_history_stats.csv"'

    writer = csv.writer(response)
    writer.writerow(['Course', 'Course ID', 'Program', 'Completed', 'Grade', 'Status', 'End Date'])
    for course in course_history:
        writer.writerow([course['name'], course['id'], course['program'], course['completed'], course['grade'], course['status'], course['end']])
    
    return response


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


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def client_admin_branding_settings(request, client_id, course_id):

    try:
        instance = BrandingSettings.objects.get(client_id=client_id)
    except:
        instance = None

    return render(request, 'admin/client-admin/course_branding_settings.haml', {
        'branding': instance,
        'client_id': client_id,
        'course_id': course_id,
        'learner_dashboard_enabled': settings.LEARNER_DASHBOARD_ENABLED,
        })


def load_background_image(request, image_url):
    from django.core.files.storage import default_storage
    if default_storage.exists(image_url):
        image = default_storage.open(image_url).read()
        print image
        from mimetypes import MimeTypes
        import urllib
        mime = MimeTypes()
        url = urllib.pathname2url(image_url)
        mime_type = mime.guess_type(url)
        return HttpResponse(
                image, content_type=mime_type[0]
            )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def client_admin_branding_settings_create_edit(request, client_id, course_id):

    try:
        instance = BrandingSettings.objects.get(client_id=client_id)
    except:
        instance = None

    if request.method == 'POST':
        form = BrandingSettingsForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            if int(client_id) != form.cleaned_data['client_id']:
                return render(request, '403.haml')
            form.save()

            url = reverse('client_admin_branding_settings', kwargs={
                'client_id': client_id,
                'course_id': course_id,
            })
            return HttpResponseRedirect(url)
    
    else:
        form = BrandingSettingsForm(instance=instance)

    default_colors = {
        'rule_color':settings.LEARNER_DASHBOARD_RULE_COLOR,
        'icon_color':settings.LEARNER_DASHBOARD_ICON_COLOR,
        'discover_title_color':settings.DISCOVER_TITLE_COLOR,
        'discover_author_color':settings.DISCOVER_AUTHOR_COLOR,
        'discover_rule_color':settings.DISCOVER_RULE_COLOR,
        'background_color':settings.LEARNER_DASHBOARD_BACKGROUND_COLOR,
    }

    return render(request, 'admin/client-admin/course_branding_settings_create_edit.haml', {
        'form': form,
        'instance': instance,
        'client_id': client_id,
        'course_id': course_id,
        'default_colors': default_colors,
        })


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def client_admin_branding_settings_reset(request, client_id, course_id):

    url = reverse('client_admin_branding_settings', kwargs={
        'client_id': client_id,
        'course_id': course_id,
        })

    try:
        instance = BrandingSettings.objects.get(client_id=client_id)
    except:
        return HttpResponseRedirect(url)

    instance.delete()

    return HttpResponseRedirect(url)


@ajaxify_http_redirects
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def client_admin_course_learner_dashboard_discover_create_edit(request, client_id, course_id, discovery_id=None):

    error = None

    try:
        learner_dashboard = LearnerDashboard.objects.get(client_id=client_id, course_id=course_id)
    except: 
        return render(request, '404.haml')

    if discovery_id:
        discovery = LearnerDashboardDiscovery.objects.get(id=discovery_id)

        url = reverse('client_admin_course_learner_dashboard_discover_create_edit', kwargs={
            'client_id': client_id,
            'course_id': course_id,
            'discovery_id': discovery.id,
            })
    else:
        discovery = None

        url = reverse('client_admin_course_learner_dashboard_discover_create_edit', kwargs={
            'client_id': client_id,
            'course_id': course_id,
            })

    if request.method == 'POST':
        form = DiscoveryContentCreateForm (request.POST, instance=discovery)
        if form.is_valid():
            form.save()

            url_list = reverse('client_admin_course_learner_dashboard_discover_list', kwargs={
                'client_id': client_id,
                'course_id': course_id,
            })

            return HttpResponseRedirect(url_list)

    else:
        form = DiscoveryContentCreateForm(instance=discovery)        

    data = {
        'url': url,
        'error': error,
        'form': form,
        'client_id': client_id,
        'course_id': course_id,
        'discovery_id': discovery_id,
        'learner_dashboard': learner_dashboard.id,
        }

    return render(
        request,
        'admin/client-admin/learner_dashboard_discovery_create_edit.haml',
        data
    )


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def client_admin_course_learner_dashboard_discover_list(request, client_id, course_id):

    learner_dashboard = LearnerDashboard.objects.get(client_id=client_id, course_id=course_id)
    discovery = LearnerDashboardDiscovery.objects.filter(learner_dashboard_id=learner_dashboard.id).order_by('position')

    return render(request, 'admin/client-admin/learner_dashboard_discovery_list.haml', {
        'client_id': client_id,
        'course_id': course_id,
        'discovery': discovery,
        'learner_dashboard_enabled': settings.LEARNER_DASHBOARD_ENABLED,
        })


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def client_admin_course_learner_dashboard_discover_delete(request, client_id, course_id, discovery_id):

    try:
        discovery = LearnerDashboardDiscovery.objects.get(id=discovery_id)
    except:
        return render(request, '404.haml')

    discovery.delete()

    url = reverse('client_admin_course_learner_dashboard_discover_list', kwargs={
        'client_id': client_id,
        'course_id': course_id,
    })

    return HttpResponseRedirect(url)


def client_admin_course_learner_dashboard_discover_reorder(request, course_id, client_id):

    if request.method == 'POST':

        data = request.POST
        dataDict = dict(data.iterlists())

        for index, item_id in enumerate(dataDict['position[]']):
            discoveryItem = LearnerDashboardDiscovery.objects.get(pk=item_id)
            discoveryItem.position = index
            discoveryItem.save()
        return HttpResponse('200')


class email_templates_get_and_post_api(APIView):
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, format=None):   
        list_of_email_templates = EmailTemplate.objects.all().order_by('title')
        templates = []
        for email_template in list_of_email_templates:    
            templates.append({'pk':email_template.pk, 'title':email_template.title, 'subject':email_template.subject, 'body': email_template.body})
        return Response(templates)

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def post(self, request, format=None):
        title = request.DATA.get('title', None)
        subject = request.DATA.get('subject', None)
        body = request.DATA.get('body', None)
        if title and subject and body:
            email_template = EmailTemplate.create(title=title, subject=subject, body=body)   
            email_template.save()
            return Response({'status':'ok', 'message':'Successfully added new email template!', 'data': \
                {'pk':email_template.pk,'title':email_template.title, 'subject':email_template.subject, 'body':email_template.body}})
        else:
            return Response({'status':'error', 'message':'Missing fields in email template!'})



class email_templates_put_and_delete_api(APIView):
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, pk, format=None):
        if pk:
            email_template = EmailTemplate.objects.filter(pk=pk)
            if len(email_template) > 0:
                email_template = email_template[0]
                return Response({'status':'ok', 'message':'Successfully got email template!', 'data': \
                    {'pk':email_template.pk, 'title':email_template.title, 'subject':email_template.subject, 'body': email_template.body}})
            else:
                return Response({'status':'error', 'message':"Can't find email template key!"})
        else:
            return Response({'status':'error', 'message':'Missing email template key!'}) 

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def delete(self, request, pk, format=None):
        if pk:
            selected_template = EmailTemplate.objects.filter(pk=pk)
            if len(selected_template) > 0:
                selected_template = selected_template[0]           
                selected_template.delete()
                return Response({'status':'ok', 'message':'Successfully deleted email template!', 'pk': pk})
            else:
                return Response({'status':'error', 'message':"Can't find email template key!"})
        else:
            return Response({'status':'error', 'message':'Missing email template key!'})

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def put(self, request, pk=None, format=None):
        if pk:
            selected_template = EmailTemplate.objects.filter(pk=pk)
            if len(selected_template) > 0:
                selected_template = selected_template[0]           
                title = request.DATA.get('title', None)
                subject = request.DATA.get('subject', None)
                body = request.DATA.get('body', None)
                if title:
                    selected_template.title = title
                if subject:
                    selected_template.subject = subject
                if body:
                    selected_template.body = body
                selected_template.save()
                return Response({'status':'ok', 'message':'Successfully updated email template!', 'data': \
                    {'pk':pk,'title':selected_template.title, 'subject':selected_template.subject, 'body':selected_template.body}})
            else:
                return Response({'status':'error', 'message':"Can't find email template key!"})
        else:
            return Response({'status':'error', 'message':'Missing email template key!'})


class email_send_api(APIView):
    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def post(self, request, format=None):
        data = json.loads(request.body)
        result = _send_multiple_emails(from_email = data.get('from_email', None), to_email_list = data.get('to_email_list', None), \
            subject = data.get('subject', None), email_body = data.get('email_body', None), template_id = data.get('template_id', None))
        if result == True:
            response = {'status':'ok'}
        else:
            response = {'status':'error', 'data': result}
        return Response(response)


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def companies_list(request):
    return render(request, 'admin/companies/companies_list.haml')


class companies_list_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request):
        
        include_slow_fields = request.GET.get('include_slow_fields', 'false')

        companies = []
        if include_slow_fields == 'false':
            clients = Client.list()
            for client in clients:
                company = {}
                company['name'] = vars(client)['display_name']
                company['id'] = vars(client)['id']
                company['numberParticipants'] = '.'
                company['numberCourses'] = '-'
                companies.append(company)
        elif include_slow_fields == 'true':
            for company_id in request.GET['ids'].split(','):
                requestParams = {}
                company = {}
                requestParams['organizations'] = company_id
                participants = user_api.get_filtered_users(requestParams)
                company['id'] = company_id
                company['numberParticipants'] = participants['count']
                companies.append(company)

        return Response(companies)



@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def company_details(request, company_id):

    client = Client.fetch(company_id)
    company = {}
    company['id'] = company_id
    company['name'] = vars(client)['display_name']
    requestParams = {}
    requestParams['organizations'] = company_id
    participants = user_api.get_filtered_users(requestParams)
    company['numberParticipants'] = participants['count']
    company['activeCourses'] = '-'

    invoicing = {}
    invoicingDetails = CompanyInvoicingDetails.objects.filter(company_id=int(company_id))
    if len(invoicingDetails) > 0:
        invoicing['full_name'] = invoicingDetails[0].full_name
        invoicing['title'] = invoicingDetails[0].title
        invoicing['address1'] = invoicingDetails[0].address1
        invoicing['address2'] = invoicingDetails[0].address2
        invoicing['city'] = invoicingDetails[0].city
        invoicing['state'] = invoicingDetails[0].state
        invoicing['postal_code'] = invoicingDetails[0].postal_code
        invoicing['country'] = invoicingDetails[0].country
        invoicing['po'] = invoicingDetails[0].po
        for key,value in invoicing.items():
            if invoicing[key].strip() == '':
                invoicing[key] = '-'
    else:
        invoicing['full_name'] = '-'
        invoicing['title'] = '-'
        invoicing['address1'] = '-'
        invoicing['address2'] = '-'
        invoicing['city'] = '-'
        invoicing['state'] = '-'
        invoicing['postal_code'] = '-'
        invoicing['country'] = '-'
        invoicing['po'] = '-'

    contacts= []
    companyContacts = CompanyContact.objects.filter(company_id=int(company_id))
    if len(companyContacts) > 0:
        for companyContact in companyContacts:
            contact = {}
            contact_type = companyContact.contact_type
            contact['type'] = CompanyContact.get_contact_type(int(contact_type))
            contact['type_id'] = contact_type
            contact['type_info'] = CompanyContact.get_type_description(contact_type)
            contact['full_name'] = companyContact.full_name
            contact['title'] = companyContact.title
            contact['email'] = companyContact.email
            contact['phone'] = companyContact.phone
            for key,value in contact.items():
                if contact[key].strip() == '':
                    contact[key] = '-'
            contacts.append(contact)
    else:
        for i in range(4):
            contact_type = CompanyContact.get_contact_type(i)
            type_description = CompanyContact.get_type_description(str(i))
            contact = {}
            contact['type'] = contact_type
            contact['type_id'] = i
            contact['type_info'] = type_description
            contact['full_name'] = '-'
            contact['title'] = '-'
            contact['email'] = '-'
            contact['phone'] = '-'
            contacts.append(contact)

    data = {
        'company': company,
        'contacts': contacts,
        'invoicing': invoicing
    }

    return render(request, 'admin/companies/company_details.haml', data)


class company_info_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def get(self, request, company_id):
        
        flag = request.GET.get('flag', None)
        response = {}
        if flag == 'contacts':
            response['flag'] = 'contacts'
            response['contacts'] = []
            companyContacts = CompanyContact.objects.filter(company_id=int(company_id))
            if len(companyContacts) > 0:
                for companyContact in companyContacts:
                    contact = {}
                    contact_type = companyContact.contact_type
                    contact['type'] = CompanyContact.get_contact_type(int(contact_type))
                    contact['type_id'] = contact_type
                    contact['type_info'] = CompanyContact.get_type_description(contact_type)
                    contact['full_name'] = companyContact.full_name
                    contact['title'] = companyContact.title
                    contact['email'] = companyContact.email
                    contact['phone'] = companyContact.phone
                    for key,value in contact.items():
                        if contact[key].strip() == '':
                            contact[key] = '-'
                    response['contacts'].append(contact)
            else:
                for i in range(4):
                    contact_type = CompanyContact.get_contact_type(i)
                    type_description = CompanyContact.get_type_description(contact_type[0])
                    contact = {}
                    contact['type'] = contact_type[1]
                    contact['type_id'] = contact_type[0]
                    contact['type_info'] = type_description
                    contact['full_name'] = '-'
                    contact['title'] = '-'
                    contact['email'] = '-'
                    contact['phone'] = '-'
                    response['contacts'].append(contact)
        elif flag == 'invoicing':
            response['flag'] = 'invoicing'
            response['invoicing'] = {}
            invoicingDetails = CompanyInvoicingDetails.objects.filter(company_id=int(company_id))
            if len(invoicingDetails) > 0:
                response['invoicing']['full_name'] = invoicingDetails[0].full_name
                response['invoicing']['title'] = invoicingDetails[0].title
                response['invoicing']['address1'] = invoicingDetails[0].address1
                response['invoicing']['address2'] = invoicingDetails[0].address2
                response['invoicing']['city'] = invoicingDetails[0].city
                response['invoicing']['state'] = invoicingDetails[0].state
                response['invoicing']['postal_code'] = invoicingDetails[0].postal_code
                response['invoicing']['country'] = invoicingDetails[0].country
                response['invoicing']['po'] = invoicingDetails[0].po
                for key,value in response['invoicing'].items():
                    if response['invoicing'][key].strip() == '':
                        response['invoicing'][key] = '-'
            else:
                response['invoicing']['full_name'] = '-'
                response['invoicing']['title'] = '-'
                response['invoicing']['address1'] = '-'
                response['invoicing']['address2'] = '-'
                response['invoicing']['city'] = '-'
                response['invoicing']['state'] = '-'
                response['invoicing']['postal_code'] = '-'
                response['invoicing']['country'] = '-'
                response['invoicing']['po'] = '-'
        
        return Response(response)

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def put(self, request, company_id):

        flag = request.GET.get('flag', None)
        response = {}
        data = json.loads(request.body)
        print data
        if flag == 'contacts':
            companyContacts = CompanyContact.objects.filter(company_id=int(company_id))
            if len(companyContacts) > 0:
                for contact in data['contacts']:
                    companyContact = CompanyContact.objects.filter(company_id=int(company_id), contact_type=contact['type_id'])
                    companyContact = companyContact[0]
                    companyContact.full_name = contact['full_name']
                    companyContact.title = contact['title']
                    companyContact.email = contact['email']
                    companyContact.phone = contact['phone']
                    companyContact.save()
            else:
                for contact in data['contacts']:
                    companyContact = CompanyContact.objects.create(company_id=int(company_id), contact_type=contact['type_id'])
                    companyContact.full_name = contact['full_name']
                    companyContact.title = contact['title']
                    companyContact.email = contact['email']
                    companyContact.phone = contact['phone']
                    companyContact.save()

        elif flag == 'invoicing':
            invoicingDetails = CompanyInvoicingDetails.objects.filter(company_id=int(company_id))
            if len(invoicingDetails) > 0:
                invoicingDetails = invoicingDetails[0]
                invoicingDetails.full_name = data['invoicing'][0]['full_name'].strip()
                invoicingDetails.title = data['invoicing'][0]['title'].strip()
                invoicingDetails.address1 = data['invoicing'][0]['address1'].strip()
                invoicingDetails.address2 = data['invoicing'][0]['address2'].strip()
                invoicingDetails.city = data['invoicing'][0]['city'].strip()
                invoicingDetails.state = data['invoicing'][0]['state'].strip()
                invoicingDetails.postal_code = data['invoicing'][0]['postal_code'].strip()
                invoicingDetails.country = data['invoicing'][0]['country_fullname'].strip()
                invoicingDetails.po = data['invoicing'][0]['po'].strip()
                invoicingDetails.save()
            else:
                invoicingDetails = CompanyInvoicingDetails.objects.create(company_id=int(company_id))
                invoicingDetails.full_name = data['invoicing'][0]['full_name'].strip()
                invoicingDetails.title = data['invoicing'][0]['title'].strip()
                invoicingDetails.address1 = data['invoicing'][0]['address1'].strip()
                invoicingDetails.address2 = data['invoicing'][0]['address2'].strip()
                invoicingDetails.city = data['invoicing'][0]['city'].strip()
                invoicingDetails.state = data['invoicing'][0]['state'].strip()
                invoicingDetails.postal_code = data['invoicing'][0]['postal_code'].strip()
                invoicingDetails.country = data['invoicing'][0]['country_fullname'].strip()
                invoicingDetails.po = data['invoicing'][0]['po'].strip()
                invoicingDetails.save()
        response['flag'] = flag
        return Response(response)


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
def download_company_info(request, company_id):

    client = Client.fetch(company_id)
    name = vars(client)['display_name']
    requestParams = {}
    requestParams['organizations'] = company_id
    participants = user_api.get_filtered_users(requestParams)
    numberParticipants = participants['count']
    activeCourses = '-'
    
    invoicingDetails = CompanyInvoicingDetails.objects.filter(company_id=int(company_id))
    invoicing = {}
    if len(invoicingDetails):
        invoicing['full_name'] = invoicingDetails[0].full_name
        invoicing['title'] = invoicingDetails[0].title
        invoicing['address1'] = invoicingDetails[0].address1
        invoicing['address2'] = invoicingDetails[0].address2
        invoicing['city'] = invoicingDetails[0].city
        invoicing['state'] = invoicingDetails[0].state
        invoicing['postal_code'] = invoicingDetails[0].postal_code
        invoicing['country'] = invoicingDetails[0].country
        invoicing['po'] = invoicingDetails[0].po
        for key,value in invoicing.items():
            if invoicing[key].strip() == '':
                invoicing[key] = '-'
    else:
        invoicing['full_name'] = '-'
        invoicing['title'] = '-'
        invoicing['address1'] = '-'
        invoicing['address2'] = '-'
        invoicing['city'] = '-'
        invoicing['state'] = '-'
        invoicing['postal_code'] = '-'
        invoicing['country'] = '-'
        invoicing['po'] = '-'

    contacts= []
    companyContacts = CompanyContact.objects.filter(company_id=int(company_id))
    if len(companyContacts) > 0:
        for companyContact in companyContacts:
            contact = {}
            contact_type = companyContact.contact_type
            contact['type'] = CompanyContact.get_contact_type(int(contact_type))
            contact['type_id'] = contact_type
            contact['type_info'] = CompanyContact.get_type_description(contact_type)
            contact['full_name'] = companyContact.full_name
            contact['title'] = companyContact.title
            contact['email'] = companyContact.email
            contact['phone'] = companyContact.phone
            for key,value in contact.items():
                if contact[key].strip() == '':
                    contact[key] = '-'
            contacts.append(contact)
    else:
        for i in range(4):
            contact_type = CompanyContact.get_contact_type(i)
            type_description = CompanyContact.get_type_description(str(i))
            contact = {}
            contact['type'] = contact_type
            contact['type_id'] = i
            contact['type_info'] = type_description
            contact['full_name'] = '-'
            contact['title'] = '-'
            contact['email'] = '-'
            contact['phone'] = '-'
            contacts.append(contact)


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + name.replace(' ', '_') + '_info.csv"'

    writer = csv.writer(response)
    writer.writerow([name])
    writer.writerow(['Total participants', numberParticipants])
    writer.writerow(['Active courses', activeCourses])
    writer.writerow([])
    writer.writerow(['INVOICING DETAILS'])
    writer.writerow(['Full name', invoicing['full_name']])
    writer.writerow(['Title', invoicing['title']])
    writer.writerow(['Invoicing address', invoicing['address1'], invoicing['address2'], invoicing['city'], invoicing['state'], invoicing['postal_code'], invoicing['country'].encode("utf-8")])
    writer.writerow(['PO #', invoicing['po']])
    writer.writerow([])
    writer.writerow(['CONTACTS'])
    for contact in contacts:
        writer.writerow([contact['type'], contact['full_name']])
        writer.writerow(['Title', contact['title']])
        writer.writerow(['Email', contact['email']])
        writer.writerow(['Phone', contact['phone']])
        writer.writerow([])

    return response


class company_edit_api(APIView):

    @permission_group_required_api(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN)
    def post(self, request, company_id):
        try:
            client = Client.update_and_fetch(company_id, request.DATA)
        except ApiError as err:
            error = err.message
            return Response({"status":"error", "message": error})
        return Response({"status":"ok", "message": "Company name successfully changed!"})

