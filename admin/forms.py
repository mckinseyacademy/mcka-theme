''' forms for login and registration '''
from datetime import date
from django import forms
from django.utils.translation import ugettext as _
from django.forms.extras.widgets import SelectDateWidget

from .models import Client, Program

# djano forms are "old-style" forms => causing lint errors
# pylint: disable=no-init,too-few-public-methods,super-on-old-class

THIS_YEAR = date.today().year
PROGRAM_YEAR_CHOICES = [yr for yr in range(THIS_YEAR, THIS_YEAR + 10)]


class ClientForm(forms.Form):

    ''' add a new client to the system '''
    display_name = forms.CharField(max_length=255)
    contact_name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=20)
    email = forms.CharField(max_length=255)


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
            choices=((program.id, program.display_name)
                     for program in program_list)
        )
        self.fields['places'] = forms.IntegerField(required=False)
