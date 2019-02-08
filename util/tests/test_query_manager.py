from django.test import TestCase

from courses.models import CourseMetaData
from util.query_manager import get_object_or_none


class TestQueryManager(TestCase):
    """Test case for util query manager"""

    def test_query_manager_model_object_exist(self):
        """Test when object exist"""
        test_model = CourseMetaData(course_id='abcid')
        test_model.save()
        returned_model = get_object_or_none(CourseMetaData, course_id='abcid')
        self.assertEqual(returned_model.course_id, test_model.course_id)
        self.assertEqual(returned_model, test_model)

    def test_query_manager_model_object_not_exist(self):
        """When object not exist"""
        self.assertIsNone(get_object_or_none(CourseMetaData, course_id='abx'))
