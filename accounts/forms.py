''' forms for login and activation '''
import datetime
from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

# djano forms are "old-style" forms => causing lint errors
# pylint: disable=no-init,too-few-public-methods,super-on-old-class

EDUCATION_LEVEL_CHOICES = (
    ("", "---"),
    ("p", _("Doctorate")),
    ("m", _("Master's or professional degree")),
    ("b", _("Bachelor's degree")),
    ("a", _("Associate's degree")),
    ("hs", _("Secondary/high school")),
    ("jhs", _("Junior secondary/junior high/middle school")),
    ("el", _("Elementary/primary school")),
    ("none", _("None")),
    ("other", _("Other")),
)
GENDER_CHOICES = (
    ("", "---"),
    ("f", _("Female")),
    ("m", _("Male")),
)


YEAR_CHOICES = [("", "---"),]
YEAR_CHOICES.extend([(year_string, year_string) for year_string in ["{}".format(year_value) for year_value in reversed(range(datetime.date.today().year - 100, datetime.date.today().year - 10))]])

READ_ONLY_IF_DATA_FIELDS = ["company", "full_name", "city", "country", ]


class NoSuffixLabelForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(NoSuffixLabelForm, self).__init__(*args, **kwargs)    

class LoginForm(NoSuffixLabelForm):
    ''' login form for system '''
    username = forms.CharField(max_length=255, label=mark_safe('Username <span class="required-field"></span>'))
    password = forms.CharField(widget=forms.PasswordInput(), label=mark_safe('Password <span class="required-field"></span>'))


class ActivationForm(NoSuffixLabelForm):
    ''' activation form for system '''
    #first_name = forms.CharField(max_length=255)
    #last_name = forms.CharField(max_length=255)

    email = forms.CharField(max_length=255, widget = forms.TextInput(attrs={'readonly':'readonly'}), label=mark_safe('E-mail'))
    password = forms.CharField(widget=forms.PasswordInput(), label=mark_safe('Password <span class="required-field"></span>'))
    #confirm_password = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(max_length=255, label=mark_safe('Public username <span class="required-field"></span>'))
    company = forms.CharField(max_length=255, required=False)
    full_name = forms.CharField(max_length=512, required=False)
    title = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255, required=False)
    country = forms.CharField(max_length=255, required=False)
    highest_level_of_education = forms.ChoiceField(choices=EDUCATION_LEVEL_CHOICES, required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    year_of_birth = forms.ChoiceField(choices=YEAR_CHOICES, required=False, initial=("", "---"))
    accept_terms = forms.BooleanField(required=False, label=mark_safe('I agree to the <a href="/terms" target="_blank">Terms of Service</a> and <a href="/privacy.html" target="_blank">Privacy Policy</a> <span class="required-field"></span>'))
    #accept_terms = forms.CheckboxInput()

    def __init__(self, *args, **kwargs):
        super(ActivationForm, self).__init__(*args, **kwargs)
        if isinstance(args[0], dict):
            user_data = args[0]
            for read_only in READ_ONLY_IF_DATA_FIELDS:
                if read_only in user_data:
                    self.fields[read_only].widget = forms.TextInput(attrs={'readonly':'readonly'})


    # def clean(self):
    #     ''' override clean to check for password matches '''
    #     cleaned_data = super(ActivationForm, self).clean()
    #     password_value = cleaned_data.get("password")
    #     confirm_password_value = cleaned_data.get("confirm_password")

    #     if password_value and confirm_password_value:
    #         # Only do something if both fields are valid so far.
    #         if confirm_password_value != password_value:
    #             raise forms.ValidationError(
    #                 _("Password fields do not match"),
    #                 code='password_match_fail'
    #             )
