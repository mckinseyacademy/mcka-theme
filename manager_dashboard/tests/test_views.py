import ddt
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status

from admin.tests.test_views import CourseParticipantsStatsMixin
from api_client.json_object import JsonParser
from manager_dashboard.views import ManagerReportsCourseDetailsApi


@ddt.ddt
class ManagerReportsCourseDetailsApiTest(CourseParticipantsStatsMixin, TestCase):
    """
    Test the ManagerReportsCourseDetailsApi view.
    """
    def setUp(self):
        """
        Patch the required APIs
        """
        super(ManagerReportsCourseDetailsApiTest, self).setUp()

    def patch_manager_reports(self, direct_reports):
        """
        Patch the get_reports_for_manager API with our data
        """
        api_data = [
            {
                'id': student.id,
                'username': student.username,
                'email': student.email,
            } for student in direct_reports
        ]
        api_client = self.apply_patch('manager_dashboard.views.user_api')
        api_client.get_reports_for_manager.return_value = JsonParser.from_dictionary(api_data)
        return api_client

    @ddt.data(
        ([], []),
        ([0, 2], [0, 2]),
        ([0, 2, 3], [0, 2]),
    )
    @ddt.unpack
    def test_get(self, direct_reports, expected_students):
        """
        Only the user's direct reports should be returned.
        """
        # Enroll only students 0-3, leaving student 4 unenrolled.
        self.patch_course_users(self.students[0:3], direct_reports)
        self.patch_manager_reports([self.students[idx] for idx in direct_reports])
        course_detail_url = reverse('manager_reports_course_details_api',
                                    kwargs={'course_id': str(self.course.course_id)})
        request = self.get_request(course_detail_url, self.admin_user)
        response = ManagerReportsCourseDetailsApi().get(request, self.course.course_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(expected_students))
        for idx, student_idx in enumerate(expected_students):
            self.assert_expected_result(response.data["results"][idx], student_idx)
