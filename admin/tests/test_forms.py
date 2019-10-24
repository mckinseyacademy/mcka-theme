import datetime
import ddt

from django.forms import ValidationError
from django.test import TestCase

from accounts.tests.utils import ApplyPatchMixin
from admin.forms import (ClientForm, ProgramForm, CreateAccessKeyForm, ShareAccessKeyForm, MultiEmailField,
                         MobileBrandingForm, ProgramAssociationForm, CourseRunForm, CustomSelectDateWidget,
                         PROGRAM_YEAR_CHOICES, BasePermissionForm, LearnerDashboardTileForm,
                         DashboardAdminQuickFilterForm)
from admin.models import LearnerDashboard, DashboardAdminQuickFilter
from admin.tests.utils import make_side_effect_raise_value_error
from lib.utils import DottableDict


class AdminFormsTests(TestCase):
    ''' Test Admin Forms '''

    def test_client_form(self):
        # valid if data is good
        client_data = {
            "display_name": "company",
            "contact_name": "contact_name",
            "contact_phone": "phone",
            "contact_email": "email@email.com",
        }
        client_form = ClientForm(client_data)

        self.assertTrue(client_form.is_valid())

    def test_program_form(self):
        # valid if data is good
        program_data = {
            "display_name": "public_name",
            "name": "private_name",
            "start_date": datetime.datetime(2014, 1, 1),
            "end_date": datetime.datetime(2014, 12, 12),
        }
        program_form = ProgramForm(program_data)

        self.assertTrue(program_form.is_valid())

    def test_create_access_key_form(self):
        # valid if data is good
        form_data = {
            "client_id": 1,
            "name": "Test Key",
            "program_id": "",
            "course_id": "",
        }
        form = CreateAccessKeyForm(form_data)
        self.assertTrue(form.is_valid())

    def test_share_access_key_form(self):
        # valid if data is good
        form_data = {
            "recipients": "student1@testorg.org, student2@testorg.org",
            "message": "",
        }
        form = ShareAccessKeyForm(form_data)
        self.assertTrue(form.is_valid())

    def test_mobile_branding_form_valid(self):
        ''' Test MobileBrandingForm with valid data '''

        form_data_valid = {
            'completed_course_tint': '#111AAA',
            'header_background_color': '#2aABCCDF',
            'lesson_navigation_color': '#aaaAAA',
            'navigation_text_color': '#1234BC12',
            'navigation_icon_color': '#FFFFFF',
        }
        form = MobileBrandingForm(form_data_valid)
        self.assertTrue(form.is_valid())

    def test_mobile_branding_form_invalid(self):
        ''' Test MobileBrandingForm with invalid data '''

        form_data_invalid = {
            'completed_course_tint': '111AAA',
            'header_background_color': '#2aABCCDFa',
            'lesson_navigation_color': '#aaa',
            'navigation_text_color': '#1ETYUU',
            'navigation_icon_color': '#zzzzzzzz',
        }
        form = MobileBrandingForm(form_data_invalid)
        self.assertFalse(form.is_valid())


class MultiEmailFieldTest(TestCase):
    def test_validation(self):
        f = MultiEmailField()
        self.assertRaisesMessage(ValidationError, "'This field is required.'", f.clean, None)
        self.assertRaisesMessage(ValidationError, "'This field is required.'", f.clean, '')
        self.assertRaisesMessage(ValidationError, "'Enter a valid email address (not-an-email-adress).'",
                                 f.clean, 'test1@testorg.org,  not-an-email-adress, test2@testorg.org')

    def test_normalization(self):
        f = MultiEmailField()
        self.assertEqual(f.clean('test1@testorg.org, test2@testorg.org'),
                         ['test1@testorg.org', 'test2@testorg.org'])
        self.assertEqual(f.clean(' test1@testorg.org  ,  ,, test2@testorg.org,,'),
                         ['test1@testorg.org', 'test2@testorg.org'])


class TestProgramAssociationForm(TestCase):

    def setUp(self):
        self.program_list = [
            DottableDict({'id': 1, 'display_name': 'Program Abc', 'name': 'abc'}),
            DottableDict({'id': 2, 'display_name': 'Program XYZ', 'name': 'xyz'})
        ]

    def test_with_valid_data(self):
        test_data = {'select_program': '1', 'places': '1'}
        self.program_association_form = ProgramAssociationForm(self.program_list, data=test_data)
        self.assertTrue(self.program_association_form.is_valid())

    def test_with_invalid_program(self):
        test_data = {'select_program': 'zxcz', 'places': '1'}
        self.program_association_form = ProgramAssociationForm(self.program_list, data=test_data)
        self.assertFalse(self.program_association_form.is_valid())

    def test_with_invalid_places(self):
        test_data = {'select_program': '1', 'places': '0'}
        self.program_association_form = ProgramAssociationForm(self.program_list, data=test_data)
        self.assertFalse(self.program_association_form.is_valid())


@ddt.ddt
class TestCourseRunForm(TestCase, ApplyPatchMixin):

    def setUp(self):
        self.course_run = {
            'name': 'test',
            'course_id': 'test/test/test',
            'email_template_new': 'sample_template',
            'email_template_existing': 'sample_template',
            'email_template_mcka': 'sample_template',
            'email_template_closed': 'sample_template',
            'self_registration_page_heading': 'Sample Header',
            'self_registration_description_text': 'Sample Description',
        }
        self.get_course = self.apply_patch('admin.forms.course_api.get_course_v1')

    @ddt.data(1, 10, 1000, 5000)
    def test_with_valid_max_participants(self, max_participants):
        self.get_course.return_value = self.course_run.get('course_id')
        self.course_run['max_participants'] = max_participants
        form = CourseRunForm(data=self.course_run)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_max_participants(), max_participants)

    @ddt.data(-1, 0, 5001, 10000)
    def test_with_invalid_max_participants(self, max_participants):
        self.get_course.return_value = self.course_run.get('course_id')
        self.course_run['max_participants'] = max_participants
        form = CourseRunForm(data=self.course_run)
        if not form.is_valid() and form.cleaned_data.get("max_participants"):
            with self.assertRaises(ValidationError):
                form.clean_max_participants()

    def test_with_invalid_course_id(self):
        self.get_course.side_effect = make_side_effect_raise_value_error()
        self.course_run['max_participants'] = 1
        form = CourseRunForm(data=self.course_run)
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValidationError):
            form.clean_course_id()


class TestCustomSelectDateWidget(TestCase):

    def setUp(self):
        self.custom_select_data_widget = CustomSelectDateWidget(
            empty_label=("---", "---", "---"),
            years=PROGRAM_YEAR_CHOICES
        )

    def test_months(self):
        expected_months = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December'
        }
        self.assertEqual(self.custom_select_data_widget.months, expected_months)

    def test_years(self):
        expected_years = PROGRAM_YEAR_CHOICES
        self.assertEqual(self.custom_select_data_widget.years, expected_years)


class TestBasePermissionForm(TestCase):

    def setUp(self):
        self.courses = [
            DottableDict({
                'id': '123/123/123',
                'name': 'sample course',
                'display_id': '123/123/123'
            }),
            DottableDict({
                'id': 'xyz/xyz/xyz',
                'name': 'sample course 2',
                'display_id': 'xyz/xyz/xyz'
            }),
        ]
        self.base_form = BasePermissionForm(courses=self.courses)

    def test_available_roles(self):
        roles = self.base_form.available_roles()
        self.assertEqual(roles[0], ('assistant', 'TA'))
        self.assertEqual(roles[1], ('observer', 'OBSERVER'))
        self.assertEqual(roles[2], ('instructor', 'MODERATOR'))

    def test_per_course_roles(self):
        per_course_roles = self.base_form.per_course_roles()
        self.assertEqual(per_course_roles[0].name, '123/123/123')
        self.assertEqual(per_course_roles[1].name, 'xyz/xyz/xyz')


@ddt.ddt
class TestLearnerDashboardTileForm(TestCase):

    def setUp(self):
        self.learner_dashboard = LearnerDashboard(
            title='sample',
            description='sample tile',
            title_color='red',
            description_color='black',
            client_id=1,
            course_id='123/123/123'
        )
        self.learner_dashboard.save()
        self.learner_dashboard_tile_form = {
            'track_progress': '',
            'label': 'sample label',
            'title': 'sample title',
            'note': 'sample note',
            'link': 'https://samplelink.com',
            'learner_dashboard': self.learner_dashboard.id,
            'label_color': 'red',
            'title_color': 'blue',
            'note_color': 'green',
            'tile_background_color': 'black',
            'download_link': 'https://samplelink.com',
            'publish_date': '',
            'background_image': '',
            'start_date': '',
            'end_date': '',
            'show_in_calendar': True,
            'show_in_dashboard': True,
            'hidden_from_learners': False,
            'fa_icon': '',
            'row': '1',
        }

    def test_with_valid_data(self):
        self.learner_dashboard_tile_form['tile_type'] = '1'
        form = LearnerDashboardTileForm(data=self.learner_dashboard_tile_form)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean(), form.cleaned_data)

    @ddt.data('2', '3', '4')
    def test_with_invalid_data(self, tile_type):
        self.learner_dashboard_tile_form['tile_type'] = tile_type
        form = LearnerDashboardTileForm(data=self.learner_dashboard_tile_form)
        self.assertFalse(form.is_valid())


class TestDashboardAdminQuickFilterForm(TestCase):

    def setUp(self):
        self.dashboard_admin_admin_quick_filter = {
            'program_id': 1,
            'course_id': 'xyz/xyz/xyz',
            'company_id': 1,
            'group_work_project_id': 'xyz',
        }

    def test_with_valid_input(self):
        form = DashboardAdminQuickFilterForm(data=self.dashboard_admin_admin_quick_filter)
        self.assertTrue(form.is_valid())
        dashboard_admin_filter, result = form.save_model_if_unique(1)
        expected_dashboard_admin_filter = DashboardAdminQuickFilter.objects.get(user_id=1)
        self.assertEqual(dashboard_admin_filter, expected_dashboard_admin_filter)
        self.assertTrue(result)
