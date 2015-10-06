import datetime
import os

from django.conf import settings
from django.utils.translation import ugettext as _

from admin.controller import assign_student_to_client_threaded
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


def process_access_key(user, access_key, client):
    """
    Processes access key for a user:
    * Adds user to a company (if not already added to other company, otherwise fails)
    * If program_id and course_id are specified - enrolls student into a course
    """
    company_ids = [company.id for company in user_api.get_user_organizations(user.id)]
    if client.id not in company_ids:
        # Associate the user with their client/company:
        assign_student_to_client_threaded(user.id, client.id, wait=True)

    # Associate the user with their program and/or course:
    if access_key.program_id:
        return assign_student_to_program(
            user, client, program_id=access_key.program_id, course_ids=[access_key.course_id]
        )

    return []  # never return None from a method that normally returns a list


def assign_student_to_program(user, client, program_id, course_ids=None):
    """
    Assign the given user to the specified client, program, and/or course.
    If any errors occur, they will be returned via django-messages.
    """
    error_messages = []
    program = Program.fetch(program_id)
    program.courses = program.fetch_courses()

    allocated, assigned = license_controller.licenses_report(program.id, client.id)
    remaining = allocated - assigned
    if remaining <= 0:
        error_messages.append(
            _("Unable to enroll you in the requested program, {}. No remaining places.").format(program.display_name)
        )
        return error_messages

    already_enrolled = Program.user_program_list(user.id)
    if program not in already_enrolled:
        program.add_user(client.id, user.id)
    if course_ids:
        valid_course_ids = set(c.course_id for c in program.fetch_courses())
        for course_id in course_ids:
            if course_id in valid_course_ids:
                try:
                    user_api.enroll_user_in_course(user.id, course_id)
                except ApiError as e:
                    error_messages.append(
                        _('Unable to enroll you in course "{}". API Error code {}.').format(course_id, e.code)
                    )
            else:
                error_messages.append(
                    _('Unable to enroll you in course "{}" - it is no longer part of your program.').format(course_id)
                )

    return error_messages
