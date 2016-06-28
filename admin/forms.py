''' forms for administration objects '''
from datetime import date
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import Client, Program, AccessKey, DashboardAdminQuickFilter, BrandingSettings, LearnerDashboardDiscovery, LearnerDashboardTile
from main.models import CuratedContentItem
from api_client.user_api import USER_ROLES
from api_client.group_api import PERMISSION_GROUPS
from api_client.json_object import JsonObjectWithImage

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

class ProgramForm(forms.Form):

    ''' add a new program to the system '''
    display_name = forms.CharField(max_length=255)
    name = forms.CharField(max_length=255)
    start_date = forms.DateField(
        widget=SelectDateWidget(years=PROGRAM_YEAR_CHOICES)
    )
    end_date = forms.DateField(
        widget=SelectDateWidget(years=PROGRAM_YEAR_CHOICES)
    )


class UploadStudentListForm(forms.Form):

    ''' form to upload file for student list '''
    student_list = forms.FileField(help_text="ClientStudentList.csv")

class MassStudentListForm(forms.Form):

    ''' form to upload file for student list '''
    student_list = forms.FileField(help_text="ClientStudentList.csv")


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


class CreateAccessKeyForm(forms.ModelForm):
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

class EditExistingUserForm(forms.Form):
    first_name = forms.CharField(required=True, widget=forms.TextInput())
    last_name = forms.CharField(required=True, widget=forms.TextInput())
    username = forms.CharField(required=False, widget=forms.TextInput())
    email = forms.EmailField(required=True, widget=forms.TextInput())
    company = forms.CharField(required=True, widget=forms.TextInput())
    gender = forms.CharField(required=False, widget=forms.TextInput())
    country = forms.CharField(required=False, widget=forms.TextInput())
    city = forms.CharField(required=False, widget=forms.TextInput())

class CreateNewParticipant(forms.Form):
    first_name = forms.CharField(required=True, widget=forms.TextInput())
    last_name = forms.CharField(required=True, widget=forms.TextInput())
    email = forms.EmailField(required=True, widget=forms.TextInput())
    company = forms.CharField(required=True, widget=forms.TextInput())
    gender = forms.CharField(required=False, widget=forms.TextInput())
    country = forms.CharField(required=False, widget=forms.TextInput())
    city = forms.CharField(required=False, widget=forms.TextInput())

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
            'client_id'
        ]
        widgets = {
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'rule_color': forms.TextInput(attrs={'type': 'color'}),
            'icon_color': forms.TextInput(attrs={'type': 'color'}),
            'discover_title_color': forms.TextInput(attrs={'type': 'color'}),
            'discover_author_color': forms.TextInput(attrs={'type': 'color'}),
            'discover_rule_color': forms.TextInput(attrs={'type': 'color'})
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

class LearnerDashboardTileForm(forms.ModelForm):
    
	class Meta:
		model = LearnerDashboardTile
		fields = [
            'label',
            'title',
            'note',
            'link',
            'tile_type',
            'background_image',
            'learner_dashboard',
            'label_color',
            'title_color',
            'note_color',
            'tile_background_color',
       	]
       	widgets = {
       		'learner_dashboard': forms.TextInput(attrs={'type': 'hidden'}),
			'link': forms.TextInput(attrs={'type': 'url'}),
            'label_color': forms.TextInput(attrs={'type': 'color'}),
            'title_color': forms.TextInput(attrs={'type': 'color'}),
            'note_color': forms.TextInput(attrs={'type': 'color'}),
            'tile_background_color': forms.TextInput(attrs={'type': 'color'}),
        }
