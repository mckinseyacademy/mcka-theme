''' forms for login and activation '''
from django import forms
from django.utils.translation import ugettext as _

# djano forms are "old-style" forms => causing lint errors
# pylint: disable=no-init,too-few-public-methods,super-on-old-class

EDUCATION_LEVEL_CHOICES = (
    (" ", "---"),
    ("p", "Doctorate"),
    ("m", "Master's or professional degree"),
    ("b", "Bachelor's degree"),
    ("a", "Associate's degree"),
    ("hs", "Secondary/high school"),
    ("jhs", "Junior secondary/junior high/middle school"),
    ("el", "Elementary/primary school"),
    ("none", "None"),
    ("other", "Other"),
)


class LoginForm(forms.Form):
    ''' login form for system '''
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())


class ActivationForm(forms.Form):
    ''' activation form for system '''
    #first_name = forms.CharField(max_length=255)
    #last_name = forms.CharField(max_length=255)

    email = forms.CharField(max_length=255, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    full_name = forms.CharField(max_length=512)
    city = forms.CharField(max_length=255)
    country = forms.CharField(max_length=255)

    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    highest_level_of_education = forms.ChoiceField(choices=EDUCATION_LEVEL_CHOICES)

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
