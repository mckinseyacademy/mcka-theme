''' forms for administration objects '''
from datetime import date
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import (
    Client, Program, AccessKey, DashboardAdminQuickFilter, 
    BrandingSettings, LearnerDashboardDiscovery, LearnerDashboardTile,
    LearnerDashboardBranding, CourseRun
)
from main.models import CuratedContentItem
from api_client import course_api
from api_client.user_api import USER_ROLES
from api_client.group_api import PERMISSION_GROUPS
from api_client.json_object import JsonObjectWithImage
from util.validators import UsernameValidator, AlphanumericWithAccentedChars

from django.forms import CharField

# djano forms are "old-style" forms => causing lint errors
# pylint: disable=no-init,too-few-public-methods,super-on-old-class

THIS_YEAR = date.today().year
PROGRAM_YEAR_CHOICES = [yr for yr in range(THIS_YEAR, THIS_YEAR + 10)]


class ClientForm(forms.Form):

    ''' add a new client to the system '''
    logo_url = forms.CharField(max_length=255, initial='', required=False)
    display_name = forms.CharField(max_length=255)
    contact_name = forms.CharField(max_length=255)
    contact_phone = forms.CharField(max_length=20)
    contact_email = forms.EmailField()
    identity_provider = forms.CharField(max_length=200, required=False)


class EditEmailForm(forms.Form):
    ''' Used to edit a user's email address. '''
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': _("Enter new email address")}))

class CustomSelectDateWidget(SelectDateWidget):

    def create_select(self, *args, **kwargs):
        old_state = self.is_required
        self.is_required = False
        result = super(CustomSelectDateWidget, self).create_select(*args, **kwargs)
        self.is_required = old_state
        return result

class ProgramForm(forms.Form):

    ''' add a new program to the system '''
    display_name = forms.CharField(max_length=255)
    name = forms.CharField(max_length=255)
    start_date = forms.DateField(
        widget=CustomSelectDateWidget(
            empty_label=("---", "---", "---"),
            years=PROGRAM_YEAR_CHOICES
            )
    )
    end_date = forms.DateField(
        widget=CustomSelectDateWidget(
            empty_label=("---", "---", "---"),
            years=PROGRAM_YEAR_CHOICES
            )
    )


class UploadStudentListForm(forms.Form):

    ''' form to upload file for student list '''
    student_list = forms.FileField(help_text="ClientStudentList.csv")

class MassStudentListForm(forms.Form):

    ''' form to upload file for student list '''
    student_list = forms.FileField(help_text="ClientStudentList.csv")

class MassParticipantsEnrollListForm(forms.Form):

    ''' form to upload file for student list '''
    student_enroll_list = forms.FileField(help_text="ParticipantsCourseList.csv")

class ProgramAssociationForm(forms.Form):

    ''' form to select program to add to client '''
    def __init__(self, program_list, *args, **kwargs):
        super(ProgramAssociationForm, self).__init__(*args, **kwargs)
        self.fields['select_program'] = forms.ChoiceField(
            choices=((program.id, "{} ({})".format(program.display_name, program.name))
                     for program in program_list)
        )
        self.fields['places'] = forms.IntegerField(min_value=1)


class CuratedContentItemForm(forms.ModelForm):
    ''' add a new curated content item for a given course '''
    class Meta:
        model = CuratedContentItem
        fields = [
            'course_id', 'content_type', 'title',
            'body', 'source', 'byline', 'byline_title', 'url',
            'thumbnail_url', 'image_url', 'twitter_username', 'sequence',
            'display_date', 'created_at'
        ]


class BasePermissionForm(forms.Form):
    ''' edit roles for a single user '''
    _per_course_roles = []

    def available_roles(self):
        return ((USER_ROLES.TA, _("TA")), (USER_ROLES.OBSERVER, _("OBSERVER")))

    def per_course_roles(self):
        return [self[name] for name in self._per_course_roles]

    def __init__(self, courses, *args, **kwargs):
        super(BasePermissionForm, self).__init__(*args, **kwargs)

        for course in courses:
            self.fields[course.id] = forms.MultipleChoiceField(
                required=False,
                label="{} ({})".format(course.name, course.display_id),
                widget=forms.CheckboxSelectMultiple,
                choices=self.available_roles()
            )

        self._per_course_roles = [course.id for course in courses]

class AdminPermissionForm(BasePermissionForm):
    permissions = forms.MultipleChoiceField(
        required=False,
        label='',
        widget=forms.CheckboxSelectMultiple,
        choices=[
            (PERMISSION_GROUPS.MCKA_ADMIN, _("ADMIN")),
            (PERMISSION_GROUPS.MCKA_SUBADMIN, _("COURSE OPS")),
            (PERMISSION_GROUPS.INTERNAL_ADMIN, _("INTERNAL ADMIN")),
            (PERMISSION_GROUPS.CLIENT_ADMIN, _("COMPANY ADMIN"))
        ]
    )

class SubAdminPermissionForm(BasePermissionForm):
    permissions = forms.MultipleChoiceField(
        required=False,
        label='',
        widget=forms.CheckboxSelectMultiple,
        choices=[
            (PERMISSION_GROUPS.MCKA_SUBADMIN, _("COURSE OPS")),
            (PERMISSION_GROUPS.INTERNAL_ADMIN, _("INTERNAL ADMIN")),
            (PERMISSION_GROUPS.CLIENT_ADMIN, _("COMPANY ADMIN"))
        ]
    )

class UploadCompanyImageForm(forms.Form):
    ''' form to upload file for company image '''
    company_image = forms.FileField(label='', help_text="Formats accepted: JPG, PNG and GIF", required=False)


class MultiEmailField(forms.Field):
    """ Comma separated email list """
    def to_python(self, value):
        "Normalize data to a list of strings."

        # Return an empty list if no input was given.
        if not value:
            return []
        # Remove empty strings and strip all spaces
        return filter(None, [email.strip() for email in value.split(",")])

    def validate(self, value):
        "Check if value consists only of valid emails."

        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).validate(value)

        invalid_emails = []

        for email in value:
            try:
                validate_email(email)
            except ValidationError as e:
                invalid_emails.append(email)

        if invalid_emails:
            message = _('Enter a valid email address ({}).').format(', '.join(invalid_emails))
            raise ValidationError(message, code=validate_email.code)


class ShareAccessKeyForm(forms.Form):
    access_key_link = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': True}))
    recipients = MultiEmailField(required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Email(s) separated by commas')}))
    message = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'placeholder': _('Message (optional)')}))


class CreateCourseAccessKeyForm(forms.ModelForm):
    class Meta:
        model = AccessKey
        fields = ['name', 'course_id']
        labels = {
            'name': _('Name'),
            'course_id': _('Course Instance'),
        }
        widgets = {
            'course_id': forms.Select,
        }
        labels = {
            'name': mark_safe('Name <span class="required-field"></span>')
        }

class CreateAccessKeyForm(forms.ModelForm):
    class Meta:
        model = AccessKey
        fields = ['name', 'program_id', 'course_id']
        labels = {
            'name': _('Name'),
            'program_id': _('Program'),
            'course_id': _('Course Instance'),
        }
        widgets = {
            'program_id': forms.Select,
            'course_id': forms.Select,
        }
        labels = {
            'name': mark_safe('Name <span class="required-field"></span>')
        }

class EditExistingUserForm(forms.Form):
    first_name = forms.CharField(required=True, widget=forms.TextInput(), validators=[AlphanumericWithAccentedChars()])
    last_name = forms.CharField(required=True, widget=forms.TextInput(), validators=[AlphanumericWithAccentedChars()])
    username = forms.CharField(required=False, widget=forms.TextInput(), validators=[UsernameValidator()])
    email = forms.EmailField(required=True, widget=forms.TextInput())
    company = forms.CharField(required=True, widget=forms.TextInput())
    gender = forms.CharField(required=False, widget=forms.TextInput())
    country = forms.CharField(required=False, widget=forms.TextInput())
    city = forms.CharField(required=False, widget=forms.TextInput(), validators=[AlphanumericWithAccentedChars()])

class CreateNewParticipant(forms.Form):
    first_name = forms.CharField(required=True, widget=forms.TextInput(), validators=[AlphanumericWithAccentedChars()])
    last_name = forms.CharField(required=True, widget=forms.TextInput(), validators=[AlphanumericWithAccentedChars()])
    email = forms.EmailField(required=True, widget=forms.TextInput())
    company = forms.CharField(required=True, widget=forms.TextInput())
    gender = forms.CharField(required=False, widget=forms.TextInput())
    country = forms.CharField(required=False, widget=forms.TextInput())
    city = forms.CharField(required=False, widget=forms.TextInput(), validators=[AlphanumericWithAccentedChars()])

class DashboardAdminQuickFilterForm(forms.ModelForm):

    class Meta:
        model = DashboardAdminQuickFilter
        fields = [
            'program_id', 'course_id', 'company_id', 'group_work_project_id'
        ]

    def save_model_if_unique(self, user_id):
        data = self.cleaned_data
        return DashboardAdminQuickFilter.objects.get_or_create(
            user_id=user_id, program_id=data['program_id'],
            course_id=data['course_id'], company_id=data.get('company_id'),
            group_work_project_id=data.get('group_work_project_id')
        )

class BrandingSettingsForm(forms.ModelForm):

    class Meta:
        model = BrandingSettings
        fields = [
            'background_image',
            'background_style',
            'background_color',
            'icon_color',
            'logo_image',
            'rule_color',
            'discover_title_color',
            'discover_author_color',
            'discover_rule_color',
            'client_id',
            'top_bar_color'
        ]
        widgets = {
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'rule_color': forms.TextInput(attrs={'type': 'color'}),
            'icon_color': forms.TextInput(attrs={'type': 'color'}),
            'discover_title_color': forms.TextInput(attrs={'type': 'color'}),
            'discover_author_color': forms.TextInput(attrs={'type': 'color'}),
            'discover_rule_color': forms.TextInput(attrs={'type': 'color'}),
            'top_bar_color': forms.TextInput(attrs={'type': 'color'})
        }

class DiscoveryContentCreateForm(forms.ModelForm):

    class Meta:
        model = LearnerDashboardDiscovery
        fields = [
            'link', 'title', 'author', 'learner_dashboard'
        ]
        widgets = {
            'learner_dashboard': forms.TextInput(attrs={'type': 'hidden'}),
            'link': forms.TextInput(attrs={'type': 'url'}),
        }


class LearnerDashboardBrandingForm(forms.ModelForm):

    class Meta:
        model = LearnerDashboardBranding
        fields = [
            'background_image',
            'background_style',
            'background_color',
            'icon_color',
            'logo_image',
            'rule_color',
            'discover_title_color',
            'discover_author_color',
            'discover_rule_color',
            'learner_dashboard',
            'top_bar_color'
        ]
        widgets = {
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'rule_color': forms.TextInput(attrs={'type': 'color'}),
            'icon_color': forms.TextInput(attrs={'type': 'color'}),
            'discover_title_color': forms.TextInput(attrs={'type': 'color'}),
            'discover_author_color': forms.TextInput(attrs={'type': 'color'}),
            'discover_rule_color': forms.TextInput(attrs={'type': 'color'}),
            'top_bar_color': forms.TextInput(attrs={'type': 'color'})
        }


class LearnerDashboardTileForm(forms.ModelForm):

	class Meta:
		model = LearnerDashboardTile
		fields = [
            'track_progress',
            'label',
            'title',
            'note',
            'publish_date',
            'link',
            'tile_type',
            'background_image',
            'learner_dashboard',
            'label_color',
            'title_color',
            'note_color',
            'tile_background_color',
            'download_link',
            'start_date',
            'end_date',
            'show_in_calendar',
            'show_in_dashboard',
            'fa_icon',
            'row'
       	]

       	widgets = {
       		'learner_dashboard': forms.TextInput(attrs={'type': 'hidden'}),
			'link': forms.TextInput(attrs={'type': 'url'}),
            'label_color': forms.TextInput(attrs={'type': 'color'}),
            'title_color': forms.TextInput(attrs={'type': 'color'}),
            'note_color': forms.TextInput(attrs={'type': 'color'}),
            'tile_background_color': forms.TextInput(attrs={'type': 'color'}),
            'download_link': forms.TextInput(attrs={'type': 'url'}),
        }

        def __init__(self, *args, **kwargs):
            super(LearnerDashboardTileForm, self).__init__(*args, **kwargs)
            self.fields['label'].widget.attrs['maxlength'] = 16

        def clean(self):
            cleaned_data = super(LearnerDashboardTileForm, self).clean()
            link = cleaned_data.get("link")
            tile_type = cleaned_data.get("tile_type")

            if tile_type == "4" and "/courses/" not in link:
                raise forms.ValidationError({'link': "Link to course is not valid"})
            if tile_type == "2" and "/chapter/" not in link:
                raise forms.ValidationError({'link': "Link to lesson is not valid"})
            if tile_type == "3" and "/module/" not in link:
                raise forms.ValidationError({'link': "Link to module is not valid"})
            return self.cleaned_data


class CourseRunForm(forms.ModelForm):

    access_key_link = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': True}))
    email_template_new = forms.CharField(widget=forms.Textarea)
    email_template_existing = forms.CharField(widget=forms.Textarea)
    email_template_mcka = forms.CharField(widget=forms.Textarea)
    email_template_closed = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = CourseRun
        fields = [
            'name',
            'max_participants',
            'is_open',
            'course_id',
            'access_key_link',
            'email_template_new',
            'email_template_existing',
            'email_template_mcka',
            'email_template_closed',
        ]

    def clean_course_id(self):
        course_id = self.cleaned_data.get("course_id")
        try:
            course = course_api.get_course_shallow(course_id)
            return course_id
        except:
            raise forms.ValidationError("Course with this ID does not exist")

    def clean_max_participants(self):

        max_participants = self.cleaned_data.get("max_participants")

        if max_participants < 1:
            raise forms.ValidationError("That number is not allowed")
        if max_participants > 5000:
            raise forms.ValidationError("Number of participants is limited to 5000")

        return max_participants
