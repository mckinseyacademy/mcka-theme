from django.urls import resolve
from django.test import TestCase


class UrlsTest(TestCase):
    def test_url_patterns(self):
        resolver = resolve('/admin/')
        self.assertEqual(resolver.view_name, 'admin_home')

        resolver = resolve('/admin/course-meta-content')
        self.assertEqual(resolver.view_name, 'course_meta_content_course_list')

        resolver = resolve('/admin/not_authorized')
        self.assertEqual(resolver.view_name, 'not_authorized')

        resolver = resolve('/admin/clients/client_new')
        self.assertEqual(resolver.view_name, 'client_new')

        resolver = resolve('/admin/clients/12345')
        self.assertEqual(resolver.view_name, 'client_detail')
        self.assertEqual(resolver.kwargs['client_id'], 12345)

        resolver = resolve('/admin/clients/12345/upload_student_list')
        self.assertEqual(resolver.view_name, 'upload_student_list')
        self.assertEqual(resolver.kwargs['client_id'], 12345)

        resolver = resolve('/admin/clients/12345/download_student_list')
        self.assertEqual(resolver.view_name, 'download_student_list')
        self.assertEqual(resolver.kwargs['client_id'], 12345)

        resolver = resolve('/admin/clients/12345/program_association')
        self.assertEqual(resolver.view_name, 'program_association')
        self.assertEqual(resolver.kwargs['client_id'], 12345)

        resolver = resolve('/admin/clients/12345/add_students_to_program')
        self.assertEqual(resolver.view_name, 'add_students_to_program')
        self.assertEqual(resolver.kwargs['client_id'], 12345)

        resolver = resolve('/admin/clients/12345/add_students_to_course')
        self.assertEqual(resolver.view_name, 'add_students_to_course')
        self.assertEqual(resolver.kwargs['client_id'], 12345)

        resolver = resolve('/admin/clients/12345/other_named_detail')
        self.assertEqual(resolver.view_name, 'client_detail')
        self.assertEqual(resolver.kwargs['client_id'], '12345')
        self.assertEqual(resolver.kwargs['detail_view'], 'other_named_detail')

        resolver = resolve('/admin/clients')
        self.assertEqual(resolver.view_name, 'client_list')

        resolver = resolve('/admin/programs/program_new')
        self.assertEqual(resolver.view_name, 'program_new')

        resolver = resolve('/admin/programs/987')
        self.assertEqual(resolver.view_name, 'program_detail')
        self.assertEqual(resolver.kwargs['program_id'], 987)

        resolver = resolve('/admin/programs/987/add_courses')
        self.assertEqual(resolver.view_name, 'add_courses')
        self.assertEqual(resolver.kwargs['program_id'], '987')

        resolver = resolve('/admin/programs/987/download_program_report')
        self.assertEqual(resolver.view_name, 'download_program_report')
        self.assertEqual(resolver.kwargs['program_id'], 987)

        resolver = resolve('/admin/programs/987/other_named_detail')
        self.assertEqual(resolver.view_name, 'program_detail')
        self.assertEqual(resolver.kwargs['program_id'], '987')
        self.assertEqual(resolver.kwargs['detail_view'], 'other_named_detail')

        resolver = resolve('/admin/programs')
        self.assertEqual(resolver.view_name, 'program_list')

        resolver = resolve('/admin/api/participants/enroll_participants_from_csv')
        self.assertEqual(resolver.view_name, 'enroll_participants_from_csv')

        resolver = resolve('/admin/api/participants/import_participants')
        self.assertEqual(resolver.view_name, 'import_participants')
