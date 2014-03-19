from django import forms
from django.utils.translation import ugettext as _


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=255)
    email = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password_value = cleaned_data.get("password")
        confirm_password_value = cleaned_data.get("confirm_password")

        if password_value and confirm_password_value:
            # Only do something if both fields are valid so far.
            if confirm_password_value != password_value:
                raise forms.ValidationError(_("Password fields do not match"), code='password_match_fail')
