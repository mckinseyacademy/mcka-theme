''' forms for login and registration '''
from django import forms
from django.utils.translation import ugettext as _
from .models import Client
from datetime import date
from django.forms.extras.widgets import SelectDateWidget

# djano forms are "old-style" forms => causing lint errors
# pylint: disable=no-init,too-few-public-methods,super-on-old-class

THIS_YEAR = date.today().year
PROGRAM_YEAR_CHOICES = [yr for yr in range(THIS_YEAR, THIS_YEAR + 10)]

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name','contact_name','phone','email',]

class ProgramForm(forms.Form):
    ''' add a new client to the system '''
    name = forms.CharField(max_length=255)
    private_name = forms.CharField(max_length=255)
    start_date = forms.DateField(widget=SelectDateWidget(years=PROGRAM_YEAR_CHOICES))
    end_date = forms.DateField(widget=SelectDateWidget(years=PROGRAM_YEAR_CHOICES))

