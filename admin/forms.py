''' forms for login and registration '''
from django import forms
from django.utils.translation import ugettext as _

# djano forms are "old-style" forms => causing lint errors
# pylint: disable=no-init,too-few-public-methods,super-on-old-class

class ClientForm(forms.Form):
    ''' add a new client to the system '''
    company = forms.CharField(max_length=255)
    contact_name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=20)
    email = forms.CharField(max_length=255)

class ProgramForm(forms.Form):
    ''' add a new client to the system '''
    public_name = forms.CharField(max_length=255)
    private_name = forms.CharField(max_length=255)
    start_date = forms.DateField()
    end_date = forms.DateField()

