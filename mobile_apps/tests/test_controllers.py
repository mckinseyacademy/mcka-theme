"""
Tests for mobile_apps django app
"""
from django.test import TestCase

from accounts.tests import ApplyPatchMixin

from ..controllers import has_mobile_ready_course


class MobileAppControllerTest(TestCase, ApplyPatchMixin):
    """
    Test cases for accounts related helper methods
    """
    def setUp(self):
        """
        Sets up the test case
        """
        super(MobileAppControllerTest, self).setUp()
        self.user_courses_progress_response = [
            {
                "created": "2017-09-13T10:10:52.804706Z",
                "is_active": "true",
                "progress": 0,
                "course": {
                    "end": "null",
                    "mobile_available": "true",
                    "start": "2017-08-01T01:00:00Z",
                    "display_name": "Certificate Demo for OPS",
                    "id": "edx/CS111/2017",
                    "course_image_url": "/c4x/edx/CS111/asset/McKA_course_tile_BusStrat.png"
                }
            }
        ]

        self.get_user_courses_progress = self.apply_patch(
            'accounts.controller.get_user_courses_progress'
        )

    def test_has_mobile_ready_course_with_mobile_ready_courses(self):
        """
        Tests has_mobile_ready_course helper method when user has mobile ready courses
        """
        user_id = 4
        self.get_user_courses_progress.return_value = self.user_courses_progress_response
        self.assertTrue(has_mobile_ready_course(user_id))

    def test_has_mobile_ready_course_without_mobile_ready_courses(self):
        """
        Tests has_mobile_ready_course helper method when user has no mobile ready courses
        """
        user_id = 4
        self.get_user_courses_progress.return_value = []
        self.assertFalse(has_mobile_ready_course(user_id))
