''' forms for administration objects '''
from datetime import date
from django import forms
from django.utils.translation import ugettext as _
from django.forms.extras.widgets import SelectDateWidget

from .models import Client, Program
from main.models import CuratedContentItem
from api_client.user_api import USER_ROLES

# djano forms are "old-style" forms => causing lint errors
# pylint: disable=no-init,too-few-public-methods,super-on-old-class

THIS_YEAR = date.today().year
PROGRAM_YEAR_CHOICES = [yr for yr in range(THIS_YEAR, THIS_YEAR + 10)]


class ClientForm(forms.Form):

    ''' add a new client to the system '''
    display_name = forms.CharField(max_length=255)
    contact_name = forms.CharField(max_length=255)
    contact_phone = forms.CharField(max_length=20)
    contact_email = forms.EmailField()


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


class ProgramAssociationForm(forms.Form):

    ''' form to select program to add to client '''
    def __init__(self, program_list, *args, **kwargs):
        super(ProgramAssociationForm, self).__init__(*args, **kwargs)
        self.fields['select_program'] = forms.ChoiceField(
            choices=((program.id, "{} ({})".format(program.display_name, program.name))
                     for program in program_list)
        )
        self.fields['places'] = forms.IntegerField()


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


class PermissionForm(forms.Form):
    ''' edit roles for a single user '''
    admin = forms.BooleanField(required=False, label=_("ADMIN"))
    _per_course_roles = []

    def available_roles(self):
        return ((USER_ROLES.STAFF, _("TA")), (USER_ROLES.OBSERVER, _("OBSERVER")))

    def per_course_roles(self):
        return [self[name] for name in self._per_course_roles]

    def __init__(self, courses, *args, **kwargs):
        super(PermissionForm, self).__init__(*args, **kwargs)

        for course in courses:
            self.fields[course.id] = forms.MultipleChoiceField(
                required=False,
                label=course.name,
                widget=forms.CheckboxSelectMultiple,
                choices=self.available_roles()
            )

        self._per_course_roles = [course.id for course in courses]
