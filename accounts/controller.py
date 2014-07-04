import urllib2 as url_access
import datetime

from django.conf import settings
from django.utils.translation import ugettext as _

from api_client import user_api
from api_client.json_object import JsonParser as JP
from api_client.api_error import ApiError

from admin.models import Program
from license import controller as license_controller


CURRENT_COURSE_ID = "current_course_id"
CURRENT_PROGRAM_ID = "current_program_id"
CURRENT_PROGRAM = "current_program"

NO_PROGRAM_ID = "NO_PROGRAM"

class ActivationError(Exception):
    '''
    Exception to be thrown when an activation failure occurs
    '''
    def __init__(self, value):
        self.value = value
        super(ActivationError, self).__init__()

    def __str__(self):
        return "ActivationError '{}'".format(self.value)


def _get_user_programs(user_id):
    ''' Helper function to retrieve the user's programs '''
    return user_api.get_user_groups(user_id, 'series', group_object=Program)


def get_current_course_by_user_id(user_id):
    # TODO: Replace with logic for finding "current" course
    # For now, we just return first course
    courses = user_api.get_user_courses(user_id)
    if len(courses) > 0:
        course_id = courses[0].id
        return course_id
    return None


def get_current_course_for_user(request):
    course_id = request.session.get(CURRENT_COURSE_ID, None)

    if not course_id and request.user:
        course_id = user_api.get_user_preferences(request.user.id).get(CURRENT_COURSE_ID, None)

    if not course_id and request.user:
        course_id = get_current_course_by_user_id(request.user.id)

    return course_id

def _load_intersecting_program_courses(program, courses):
    if program.id == NO_PROGRAM_ID:
        program.courses = courses
        program.outside_courses = None
    else:
        program_course_ids = [course.course_id for course in program.fetch_courses()]
        program.courses = [course for course in courses if course.id in program_course_ids]
        program.outside_courses = [course for course in courses if course.id not in program_course_ids]

def set_current_course_for_user(request, course_id):
    prev_course_id = request.session.get(CURRENT_COURSE_ID, None)
    if prev_course_id != course_id:
        request.session[CURRENT_COURSE_ID] = course_id
        user_api.set_user_preferences(
            request.user.id,
            {
                CURRENT_COURSE_ID: course_id,
            }
        )

        # Additionally set the current program for this user
        current_program = None
        courses = user_api.get_user_courses(request.user.id)
        for program in Program.programs_with_course(course_id):
            if license_controller.fetch_granted_license(program.id, request.user.id) is not None:
                current_program = program
                break

        if current_program is None:
            # Fake program
            current_program = Program(dictionary={"id": NO_PROGRAM_ID, "name": settings.NO_PROGRAM_NAME})

        _load_intersecting_program_courses(current_program, courses)
        set_current_program_for_user(request, current_program)


def get_current_program_for_user(request):

    # Attempt to load from current session
    program = request.session.get(CURRENT_PROGRAM, None)

    # Attempt to load from user preferences
    if not program and request.user:
        program_id = user_api.get_user_preferences(request.user.id).get(CURRENT_PROGRAM_ID, None)
        if program_id == NO_PROGRAM_ID:
            program = Program(dictionary={"id": NO_PROGRAM_ID, "name": settings.NO_PROGRAM_NAME})
        elif program_id:
            program = Program.fetch(program_id)

        # if not attempt to load first program
        if not program:
            programs = _get_user_programs(request.user.id)
            if len(programs) > 0:
                program = programs[0]

        if program:
            _load_intersecting_program_courses(program, user_api.get_user_courses(request.user.id))
            set_current_program_for_user(request, program)

    # Return the program to the caller
    return program


def set_current_program_for_user(request, program):
    prev_program = request.session.get(CURRENT_PROGRAM, None)
    if prev_program is None or (prev_program.id != program.id):
        request.session[CURRENT_PROGRAM] = program
        request.session[CURRENT_PROGRAM_ID] = program.id
        user_api.set_user_preferences(
            request.user.id,
            {
                CURRENT_PROGRAM_ID: str(program.id),
            }
        )


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

def save_profile_image(request, cropped_example, image_url):

    import StringIO
    from PIL import Image
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile

    cropped_image_120 = _rescale_image(cropped_example, 120, 120)
    cropped_image_40 = _rescale_image(cropped_example, 40, 40)

    thumb_io_120 = StringIO.StringIO()
    thumb_io_40 = StringIO.StringIO()
    thumb_io = StringIO.StringIO()

    cropped_image_120.save(thumb_io_120, format='JPEG')
    cropped_image_40.save(thumb_io_40, format='JPEG')
    cropped_example.save(thumb_io, format='JPEG')

    if default_storage.exists(image_url):
        default_storage.delete(image_url)
    if default_storage.exists(image_url[:-4] + '-40.jpg'):
        default_storage.delete(image_url[:-4] + '-40.jpg')
    if default_storage.exists(image_url[:-4] + '-120.jpg'):
        default_storage.delete(image_url[:-4] + '-120.jpg')

    cropped_image_120_path = default_storage.save('images/profile_image-{}-120.jpg'.format(request.user.id), thumb_io_120)
    cropped_image_40_path = default_storage.save('images/profile_image-{}-40.jpg'.format(request.user.id), thumb_io_40)
    cropped_image_path = default_storage.save('images/profile_image-{}.jpg'.format(request.user.id), thumb_io)
    request.user._image_url = '/accounts/' + cropped_image_path
    request.user.save()
    user_api.update_user_information(request.user.id,  {'avatar_url': '/accounts/' + cropped_image_path})

    return request.user

def _rescale_image(img, width, height, force=True):
    """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""
    import Image as pil
    from cStringIO import StringIO

    max_width = width
    max_height = height

    if not force:
        img.thumbnail((max_width, max_height), pil.ANTIALIAS)
    else:
        from PIL import ImageOps
        img = ImageOps.fit(img, (max_width, max_height,), method=pil.ANTIALIAS)

    tmp = StringIO()
    img.save(tmp, 'JPEG')
    output_data = img
    tmp.close()

    return output_data
