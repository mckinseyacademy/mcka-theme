''' forms for login and activation '''
from django import forms
from django.utils.translation import ugettext as _

# djano forms are "old-style" forms => causing lint errors
# pylint: disable=no-init,too-few-public-methods,super-on-old-class

class LoginForm(forms.Form):
    ''' login form for system '''
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())


class ActivationForm(forms.Form):
    ''' activation form for system '''
    username = forms.CharField(max_length=255, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    email = forms.CharField(max_length=255, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)

    def clean(self):
        ''' override clean to check for password matches '''
        cleaned_data = super(ActivationForm, self).clean()
        password_value = cleaned_data.get("password")
        confirm_password_value = cleaned_data.get("confirm_password")

        if password_value and confirm_password_value:
            # Only do something if both fields are valid so far.
            if confirm_password_value != password_value:
                raise forms.ValidationError(
                    _("Password fields do not match"),
                    code='password_match_fail'
                )
