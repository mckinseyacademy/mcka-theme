from collections import namedtuple
import datetime
from django.contrib import messages
import os

from django.conf import settings
from django.utils.translation import ugettext as _

from admin.models import Program

from api_client import user_api, third_party_auth_api
from api_client.api_error import ApiError

from license import controller as license_controller


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
                    messages.ERROR,
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
