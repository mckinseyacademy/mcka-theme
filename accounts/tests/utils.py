''' Helper methods for accounts test
'''
from mock import patch

from accounts.models import RemoteUser
from admin.models import Program
from api_client.course_models import CourseListCourse
from api_client.organization_models import Organization


# TODO: refactor into a test utilities class

class ApplyPatchMixin(object):
    """ Mixin with patch helper method """

    def apply_patch(self, *args, **kwargs):
        """
        Applies patch and registers a callback to stop the patch in TearDown method
        """
        patcher = patch(*args, **kwargs)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock


def _make_user(username='johndoe', email='john@doe.org', password='password'):
    return RemoteUser.objects.create_user(username=username, email=email, password=password)


def _make_company(org_id, display_name='company_name'):
    return Organization(dictionary={'id': org_id, 'display_name': display_name})


def _make_program(prog_id=1, display_name='Test program', courses=None):
    courses = courses if courses else []
    program = Program(dictionary={'id': prog_id, 'display_name': display_name})
    program.courses = courses
    return program


def _make_course(course_id='course_id', display_name='Course Name'):
    return CourseListCourse(dictionary={'course_id': course_id, 'display_name': display_name})


class TestUserObject(object):
    id = None
    email = None
    task_key = None

    def __init__(self, user_id, email, task_key='test_key'):
        self.id = user_id
        self.email = email
        self.task_key = task_key
