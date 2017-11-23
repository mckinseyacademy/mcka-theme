from collections import namedtuple
from django.contrib import messages
import os, re, urllib, json, datetime

from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext as _
from django.utils.http import urlsafe_base64_encode
from django.core.urlresolvers import reverse
from django.template import loader
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from email.MIMEImage import MIMEImage
from django.utils.html import strip_tags

from admin.controller import _send_activation_email_to_single_new_user, enroll_user_in_course
from admin.models import Program, LearnerDashboard, Client
from api_client.user_api import get_user_courses_progress
from courses.user_courses import get_current_course_for_user
from courses.models import FeatureFlags

from api_client import user_api, third_party_auth_api, organization_api, course_api, mobile_api_user
from api_client.api_error import ApiError
from util.user_agent_helpers import is_ios, is_supported_mobile_device

from license import controller as license_controller
from .models import UserPasswordReset, UserActivation


COMPANIES_MOBILE_APPS_MAP = {
    # Mckinsey and Company FF
    17: {
        'android': '#',
        'ios': 'https://dappservices.mckinsey.com/mifs/asfV3x/appstore?appid=3507',
        'tagline': '',
        'background_image': '/static/image/mobile_popup/rts_bg.png',
        'logo_image': '/static/image/mobile_popup/rts_logo',
        'mobile_image': '/static/image/mobile_popup/rts_device',
        'download_banner_image': 'mobile_iron_badge'
    },
    # Chemours
    153: {
        'android': '#',
        'ios': 'https://itunes.apple.com/us/app/rts-academy/id1299877239',
        'tagline': '',
        'background_image': '/static/image/mobile_popup/rts_bg.png',
        'logo_image': '/static/image/mobile_popup/rts_logo',
        'mobile_image': '/static/image/mobile_popup/rts_device',
        'download_banner_image': 'Badge.iOSAppStore'
    }
}


class ActivationError(Exception):
    '''
    Exception to be thrown when an activation failure occurs
    '''
    def __init__(self, value):
        self.value = value
        super(ActivationError, self).__init__()

    def __str__(self):
        return "ActivationError '{}'".format(self.value)


def user_activation_with_data(user_id, user_data, activation_record):
    try:
        # Make sure they'll be inactive while updating fields, then we explicitly activate them
        user_data["is_active"] = False
        updated_user = user_api.update_user_information(user_id, user_data)
    except ApiError as e:
        raise ActivationError(e.message)

    # if we are still okay, then activate in a separate operation
    try:
        user_api.activate_user(user_id)
    except ApiError as e:
        raise ActivationError(e.message)

    activation_record.delete()


def is_future_start(date):
    current_time = datetime.datetime.now()
    if date <= current_time:
        return False
    else:
        return True

def save_new_client_image(old_image_url, new_image_url, client):

    import StringIO
    from PIL import Image
    from django.core.files.storage import default_storage

    new_image_url_name = os.path.splitext(new_image_url)[0]
    old_image_url_name = os.path.splitext(old_image_url)[0]

    if default_storage.exists(old_image_url):

        io_new_client_image(old_image_url, new_image_url)

        for generate_size in settings.COMPANY_GENERATE_IMAGE_SIZES:
            old_gen_image_url = "{}-{}.jpg".format(old_image_url_name, generate_size[0])
            new_gen_image_url = "{}-{}.jpg".format(new_image_url_name, generate_size[0])
            io_new_client_image(old_gen_image_url, new_gen_image_url)
        client.update_and_fetch(client.id,  {'logo_url': '/accounts/' + "{}.jpg".format(new_image_url_name)})

def io_new_client_image(old_gen_image_url, new_gen_image_url):

    import StringIO
    from PIL import Image
    from django.core.files.storage import default_storage

    thumb_io = StringIO.StringIO()
    original = Image.open(default_storage.open(old_gen_image_url))
    original.convert('RGB').save(thumb_io, format='JPEG')
    cropped_image_path = default_storage.save(new_gen_image_url, thumb_io)
    default_storage.delete(old_gen_image_url)


def get_sso_provider(email):
    provider_associations = third_party_auth_api.get_providers_by_email(email)

    if provider_associations:
        # provider ids are prefixed with auth type: saml, oauth, etc.
        prefixed_provider_id = provider_associations[0].provider_id
        return "-".join(prefixed_provider_id.split("-")[1:])
    else:
        return None


ProcessAccessKeyResult = namedtuple(
    'ProcessAccessKeyResult', ['enrolled_in_course_ids', 'new_enrollements_course_ids', 'messages']
)


def process_access_key(user, access_key, client):
    """
    Processes access key for a user:
    * Adds user to a company (if not already added to other company, otherwise fails)
    * If program_id and course_id are specified - enrolls student into a course
    """
    company_ids = [company.id for company in user_api.get_user_organizations(user.id)]
    if company_ids and client.id not in company_ids:
        error_message = _("Access Key {key} is associated with company {company}, "
                          "but you're not registered with it").format(key=access_key.code, company=client.display_name)
        return ProcessAccessKeyResult(
            enrolled_in_course_ids=None, new_enrollements_course_ids=None, messages=[(messages.ERROR, error_message)]
        )

    if client.id not in company_ids:
        # Associate the user with their client/company:
        client.add_user(user.id)

    # Associate the user with their program and/or course:
    processing_messages = []
    enrolled_in_course_ids = []
    new_enrollements_course_ids = []
    if access_key.program_id:
        add_to_program_result = assign_student_to_program(user, client, program_id=access_key.program_id)
        program, message = add_to_program_result.program, add_to_program_result.message
        if message:
            processing_messages.append(message)
        if program and access_key.course_id:
            enroll_in_course_result = enroll_student_in_course(user, program, access_key.course_id)
            if enroll_in_course_result.message:
                processing_messages.append(enroll_in_course_result.message)

            if enroll_in_course_result.enrolled:
                enrolled_in_course_ids.append(enroll_in_course_result.course_id)

                if enroll_in_course_result.new_enrollment:
                    new_enrollements_course_ids.append(enroll_in_course_result.course_id)
    else:
        enroll_in_course_result = enroll_student_in_course_without_program(user, access_key.course_id)
        if enroll_in_course_result.message:
            processing_messages.append(enroll_in_course_result.message)

        if enroll_in_course_result.enrolled:
            enrolled_in_course_ids.append(enroll_in_course_result.course_id)

            if enroll_in_course_result.new_enrollment:
                new_enrollements_course_ids.append(enroll_in_course_result.course_id)

    return ProcessAccessKeyResult(
        enrolled_in_course_ids=enrolled_in_course_ids, new_enrollements_course_ids=new_enrollements_course_ids,
        messages=processing_messages
    )


AssignStudentToProgramResult = namedtuple('AssignStudentToProgramResult', ['program', 'message'])
EnrollStudentInCourseResult = namedtuple(
    'EnrollStudentInCourseResult', ['course_id', 'enrolled', 'new_enrollment', 'message']
)


def assign_student_to_program(user, client, program_id):
    """
    Assign the given user to the specified client and program
    Returns AssignStudentToProgramResult, containing the program (if exists) and messages (if any)
    """
    program = Program.fetch(program_id)
    program.courses = program.fetch_courses()

    allocated, assigned = license_controller.licenses_report(program.id, client.id)
    remaining = allocated - assigned
    if remaining <= 0:
        message = (
            messages.ERROR,
            _("Unable to enroll you in the requested program, {}. No remaining places.").format(program.display_name)
        )
        return AssignStudentToProgramResult(None, message)

    already_enrolled = Program.user_program_list(user.id)
    if program not in already_enrolled:
        program.add_user(client.id, user.id)

    return AssignStudentToProgramResult(program, None)


def enroll_student_in_course(user, program, course_id):
    """
    Enroll the given user to the specified course in a program
    Returns EnrollStudentInCourseResult, containing the course_id (if exists and in program) and messages (if any)
    """
    valid_course_ids = set(c.course_id for c in program.courses)
    enrolled, new_enrollment = False, False
    if course_id in valid_course_ids:
        try:
            user_api.enroll_user_in_course(user.id, course_id)
            message = (
                messages.INFO, _("Successfully enrolled you in a course {}.").format(course_id)
            )
            enrolled, new_enrollment = True, True
        except ApiError as e:
            if e.code == 409:
                message = (
                    messages.INFO,
                    _('You are already enrolled in course "{}"').format(course_id)
                )
                enrolled = True
            else:
                message = (
                    messages.ERROR,
                    _('Unable to enroll you in course "{}".').format(course_id)
                )
    else:
        message = (
            messages.ERROR,
            _('Unable to enroll you in course "{}" - it is no longer part of your program.').format(course_id)
        )
    return EnrollStudentInCourseResult(course_id, enrolled, new_enrollment, message)


def enroll_student_in_course_without_program(user, course_id):
    """
    Enroll the given user to the specified course
    Returns EnrollStudentInCourseResult, containing the course_id (if exists) and messages (if any)
    """
    enrolled, new_enrollment = False, False
    try:
        user_api.enroll_user_in_course(user.id, course_id)
        message = (
            messages.INFO, _("Successfully enrolled you in a course {}.").format(course_id)
        )
        enrolled, new_enrollment = True, True
    except ApiError as e:
        if e.code == 409:
            message = (
                messages.INFO,
                _('You are already enrolled in course "{}"').format(course_id)
            )
            enrolled = True
        else:
            message = (
                messages.ERROR,
                _('Unable to enroll you in course "{}".').format(course_id)
            )

    return EnrollStudentInCourseResult(course_id, enrolled, new_enrollment, message)


def send_password_reset_email(
    domain, user, use_https,
    subject_template_name='registration/password_reset_subject.txt',
    email_template_name='registration/password_reset_email.html',
    from_email=settings.APROS_EMAIL_SENDER
):

    uid = urlsafe_base64_encode(force_bytes(user.id))

    reset_record = UserPasswordReset.create_record(user)

    url = reverse('reset_confirm', kwargs={'uidb64':uid, 'token': reset_record.validation_key})

    c = {
        'email': user.email,
        'domain': domain,
        'url': url,
        'user': user,
        'protocol': 'https' if use_https else 'http',
    }
    subject = loader.render_to_string(subject_template_name, c)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    email = loader.render_to_string(email_template_name, c)
    email = EmailMessage(subject, email, from_email, [user.email], headers = {'Reply-To': from_email})
    email.send(fail_silently=False)


def process_registration_request(request, user, course_run, existing_user_object=None):

    domain = request.META.get('HTTP_HOST')
    protocol = 'https' if request.is_secure() else 'http'

    if not user.new_user and not user.mcka_user:
        _process_existing_non_mcka_user(domain, protocol, user, course_run, existing_user_object)

    if user.new_user and not user.mcka_user:
        _process_new_non_mcka_user(request, user, course_run)

    if user.mcka_user:
        _process_mcka_user(request, user, course_run)

def _process_existing_non_mcka_user(domain, protocol, user, course_run, existing_user_object):

    email_template_html = "registration/public_registration_existing_non_mcka.haml"
    subject = "Welcome to McKinsey Academy"
    link = protocol + "://" + domain + "/courses/" + course_run.course_id
    template_text = course_run.email_template_existing

    enroll_in_course_result = enroll_student_in_course_without_program(existing_user_object, course_run.course_id)
    if not enroll_in_course_result.enrolled:
        raise ValueError('Problem with course enrollment')
    send_email(email_template_html, subject, link, template_text, user.first_name, existing_user_object.email)

def _process_new_non_mcka_user(request, registration_request, course_run):

    email_template_html = "registration/public_registration_activation_link.haml"
    subject = "Welcome to McKinsey Academy"
    template_text = course_run.email_template_new

    user = _register_user_on_platform(registration_request)

    if user and not user.is_active:
        link = generate_activation_link(request, user)
        if link:
            send_email(email_template_html, subject, link, template_text, registration_request.first_name, user.email)
            _get_set_company(user.id)
            enroll_user_in_course(user.id, course_run.course_id)
            course_run.total_activations_sent += 1
            course_run.save()
        else:
            raise ValueError('Activation link generation problem')

def _process_mcka_user(request, registration_request, course_run):

    email_template_html = "registration/public_registration_mcka_user.haml"
    subject = "Welcome to McKinsey Academy"
    template_text = course_run.email_template_mcka
    link = course_run.access_key_link

    send_email(email_template_html, subject, link, template_text, registration_request.first_name, registration_request.company_email)

def _process_course_run_closed(registration_request, course_run):

    email_template_html = 'registration/public_registration_course_closed.haml'
    subject = "Your request to access McKinsey Academy"
    template_text = course_run.email_template_closed
    link = None

    send_email(email_template_html, subject, link, template_text, registration_request.first_name, registration_request.company_email)


def generate_activation_link(request, user):
    activation_record = UserActivation.user_activation(user)
    absolute_activation_uri = request.build_absolute_uri('/accounts/activate')
    return "{}/{}/{}".format(absolute_activation_uri, activation_record.activation_key, "activation/")

def _get_set_company(user_id):

    companies = organization_api.get_organization_by_display_name("demo_course")

    if companies['count'] != 0:
        company = companies['results'][0]['id']
    else:
        new_company = organization_api.create_organization(organization_name="demo_course", organization_data={"display_name": "demo_course"})
        company = vars(new_company).get("id", None)

    client = Client.fetch(company)
    client.add_user(user_id)

def _register_user_on_platform(user):

    data = {}

    if len(user.company_email) > 30:
        data['username'] = user.company_email[:29]
    else:
        data['username'] = user.company_email
    data['first_name'] = user.first_name
    data['last_name'] = user.last_name
    data['email'] = user.company_email
    data['username'] = re.sub(r'\W', '', user.company_email)
    data['password'] = settings.INITIAL_PASSWORD
    data['is_active'] = False

    try:
        return user_api.register_user(data)
    except:
        raise ValueError('Api error')

def send_email(email_template_html, subject, link, template_text, user_name, user_email):

    c = {
        'username': user_name,
        'email': user_email,
        'link': link,
        'template_text': template_text,
    }
    email_html = loader.render_to_string(email_template_html, c)
    email_plain = strip_tags(email_html)

    email = EmailMultiAlternatives(
        subject,
        email_plain,
        settings.APROS_EMAIL_SENDER,
        [user_email],
        headers = {'Reply-To': settings.APROS_EMAIL_SENDER})
    email.attach_alternative(email_html, "text/html")
    email.mixed_subtype = 'related'

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    f = 'static/image/email_header.png'
    fp = open(os.path.join(BASE_DIR, f), 'rb')
    msg_img = MIMEImage(fp.read())
    fp.close()
    msg_img.add_header('Content-ID', '<{}>'.format(f))
    email.attach(msg_img)

    email.send(fail_silently=False)

def _set_number_of_enrolled_users(course_run):

    course_users = json.loads(course_api.get_user_list_json(course_run.course_id, page_size=100))
    roles_user_ids = course_api.get_users_filtered_by_role(course_run.course_id)
    exclude_user_ids = [role.id for role in roles_user_ids]
    #removing duplicates
    exclude_user_ids = list(set(exclude_user_ids))

    for user in course_users:
        if user['id'] in exclude_user_ids:
            course_users.remove(user)

    course_run.total_participants = len(course_users)
    course_run.save()
    return course_users

def send_warning_email_to_admin(course_run):

    email_template_html = 'registration/public_registration_warning.haml'
    subject = 'Demo Registration - Warning'

    c = {
        'max_participants': course_run.max_participants,
        'treshold': settings.COURSE_RUN_PARTICIPANTS_TRESHOLD,
        'course_id': course_run.course_id,
    }

    email_html = loader.render_to_string(email_template_html, c)
    email_plain = strip_tags(email_html)
    email = EmailMultiAlternatives(
        subject,
        email_plain,
        settings.APROS_EMAIL_SENDER,
        [settings.DEDICATED_COURSE_RUN_PERSON],
        headers = {'Reply-To': settings.APROS_EMAIL_SENDER})
    email.attach_alternative(email_html, 'text/html')
    email.send(fail_silently=False)


def has_mobile_ready_course(user_id):
    """
    Returns boolean based on if user has any mobile ready course
    """
    qs_params = dict(mobile_only=True)
    # TODO:  Request a dedicated API to get if user has a mobile-ready course
    #        and use that API instead of using progress api.
    response = get_user_courses_progress(user_id, qs_params)

    return True if len(response) else False


def get_mobile_app_download_popup_data(request):
    mobile_popup_data = dict()
    try:
        users = user_api.get_users(username=request.GET['username'])
        if users and has_mobile_ready_course(users[0].id):
            companies = user_api.get_user_organizations(users[0].id)
            if companies and companies[0].id in COMPANIES_MOBILE_APPS_MAP:
                mobile_popup_data['company_mobile_app_map'] = COMPANIES_MOBILE_APPS_MAP[companies[0].id]
    except ApiError:
        pass

    if is_supported_mobile_device(request) and 'company_mobile_app_map' in mobile_popup_data:
        mobile_popup_data["show_app_link_popup"] = True

    return mobile_popup_data


def append_user_mobile_app_id_cookie(response, user_id):

    organizations = user_api.get_user_organizations(user_id)

    if len(organizations) > 0:
        ios_app_id, android_app_id = get_mobile_app_id(organizations[0])

 # we will get ios and android id
        response.set_cookie(
            'ios_app_id',
            ios_app_id,
            domain=settings.LMS_SESSION_COOKIE_DOMAIN,
        )

        response.set_cookie(
            'android_app_id',
            android_app_id,
            domain=settings.LMS_SESSION_COOKIE_DOMAIN,
        )

    return response


def get_mobile_app_id(organization):

    ios_app_id = None
    android_app_id = None

    try:
        mobile_id = mobile_api_user.get_mobile_apps({"organization_id": organization.id})
        results = mobile_id['results'][0]
        ios_app_id = results['ios_app_id']
        android_app_id = results['android_app_id']
    except ApiError:
        pass

    return ios_app_id, android_app_id