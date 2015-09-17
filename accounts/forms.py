#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' forms for login and activation '''
import datetime
from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from api_client import user_api
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.html import format_html
from django.forms.util import flatatt
from django.utils.encoding import force_text
from django.core.urlresolvers import reverse
from api_client.api_error import ApiError

from .models import UserPasswordReset

# djano forms are "old-style" forms => causing lint errors
# pylint: disable=no-init,too-few-public-methods,super-on-old-class

EDUCATION_LEVEL_CHOICES = (
    ("", "---"),
    ("b", _("Bachelor's degree")),
    ("mba", _("Master's of Business Administration (MBA)")),
    ("m", _("Master's degree (non MBA)")),
    ("p", _("Doctorate (PhD)")),
    ("other", _("Other")),
)
GENDER_CHOICES = (
    ("", "---"),
    ("f", _("Female")),
    ("m", _("Male")),
)

YEAR_CHOICES = [("", "---"),]
YEAR_CHOICES.extend([(year_string, year_string) for year_string in ["{}".format(year_value) for year_value in reversed(range(datetime.date.today().year - 100, datetime.date.today().year - 10))]])

COUNTRY_CHOICES = (
    ("", "---"),
    ("AF", _(u"Afghanistan")),
    ("AX", _(u"Åland Islands")),
    ("AL", _(u"Albania")),
    ("DZ", _(u"Algeria")),
    ("AS", _(u"American Samoa")),
    ("AD", _(u"Andorra")),
    ("AO", _(u"Angola")),
    ("AI", _(u"Anguilla")),
    ("AQ", _(u"Antarctica")),
    ("AG", _(u"Antigua and Barbuda")),
    ("AR", _(u"Argentina")),
    ("AM", _(u"Armenia")),
    ("AW", _(u"Aruba")),
    ("AU", _(u"Australia")),
    ("AT", _(u"Austria")),
    ("AZ", _(u"Azerbaijan")),
    ("BS", _(u"Bahamas")),
    ("BH", _(u"Bahrain")),
    ("BD", _(u"Bangladesh")),
    ("BB", _(u"Barbados")),
    ("BY", _(u"Belarus")),
    ("BE", _(u"Belgium")),
    ("BZ", _(u"Belize")),
    ("BJ", _(u"Benin")),
    ("BM", _(u"Bermuda")),
    ("BT", _(u"Bhutan")),
    ("BO", _(u"Bolivia, Plurinational State of")),
    ("BQ", _(u"Bonaire, Sint Eustatius and Saba")),
    ("BA", _(u"Bosnia and Herzegovina")),
    ("BW", _(u"Botswana")),
    ("BV", _(u"Bouvet Island")),
    ("BR", _(u"Brazil")),
    ("IO", _(u"British Indian Ocean Territory")),
    ("BN", _(u"Brunei Darussalam")),
    ("BG", _(u"Bulgaria")),
    ("BF", _(u"Burkina Faso")),
    ("BI", _(u"Burundi")),
    ("KH", _(u"Cambodia")),
    ("CM", _(u"Cameroon")),
    ("CA", _(u"Canada")),
    ("CV", _(u"Cape Verde")),
    ("KY", _(u"Cayman Islands")),
    ("CF", _(u"Central African Republic")),
    ("TD", _(u"Chad")),
    ("CL", _(u"Chile")),
    ("CN", _(u"China")),
    ("CX", _(u"Christmas Island")),
    ("CC", _(u"Cocos (Keeling) Islands")),
    ("CO", _(u"Colombia")),
    ("KM", _(u"Comoros")),
    ("CG", _(u"Congo")),
    ("CD", _(u"Congo, The Democratic Republic of the")),
    ("CK", _(u"Cook Islands")),
    ("CR", _(u"Costa Rica")),
    ("CI", _(u"Côte D'ivoire")),
    ("HR", _(u"Croatia")),
    ("CU", _(u"Cuba")),
    ("CW", _(u"Curaçao")),
    ("CY", _(u"Cyprus")),
    ("CZ", _(u"Czech Republic")),
    ("DK", _(u"Denmark")),
    ("DJ", _(u"Djibouti")),
    ("DM", _(u"Dominica")),
    ("DO", _(u"Dominican Republic")),
    ("EC", _(u"Ecuador")),
    ("EG", _(u"Egypt")),
    ("SV", _(u"El Salvador")),
    ("GQ", _(u"Equatorial Guinea")),
    ("ER", _(u"Eritrea")),
    ("EE", _(u"Estonia")),
    ("ET", _(u"Ethiopia")),
    ("FK", _(u"Falkland Islands (Malvinas)")),
    ("FO", _(u"Faroe Islands")),
    ("FJ", _(u"Fiji")),
    ("FI", _(u"Finland")),
    ("FR", _(u"France")),
    ("GF", _(u"French Guiana")),
    ("PF", _(u"French Polynesia")),
    ("TF", _(u"French Southern Territories")),
    ("GA", _(u"Gabon")),
    ("GM", _(u"Gambia")),
    ("GE", _(u"Georgia")),
    ("DE", _(u"Germany")),
    ("GH", _(u"Ghana")),
    ("GI", _(u"Gibraltar")),
    ("GR", _(u"Greece")),
    ("GL", _(u"Greenland")),
    ("GD", _(u"Grenada")),
    ("GP", _(u"Guadeloupe")),
    ("GU", _(u"Guam")),
    ("GT", _(u"Guatemala")),
    ("GG", _(u"Guernsey")),
    ("GN", _(u"Guinea")),
    ("GW", _(u"Guinea-bissau")),
    ("GY", _(u"Guyana")),
    ("HT", _(u"Haiti")),
    ("HM", _(u"Heard Island and McDonald Islands")),
    ("VA", _(u"Holy See (Vatican City State)")),
    ("HN", _(u"Honduras")),
    ("HK", _(u"Hong Kong")),
    ("HU", _(u"Hungary")),
    ("IS", _(u"Iceland")),
    ("IN", _(u"India")),
    ("ID", _(u"Indonesia")),
    ("IR", _(u"Iran, Islamic Republic of")),
    ("IQ", _(u"Iraq")),
    ("IE", _(u"Ireland")),
    ("IM", _(u"Isle of Man")),
    ("IL", _(u"Israel")),
    ("IT", _(u"Italy")),
    ("JM", _(u"Jamaica")),
    ("JP", _(u"Japan")),
    ("JE", _(u"Jersey")),
    ("JO", _(u"Jordan")),
    ("KZ", _(u"Kazakhstan")),
    ("KE", _(u"Kenya")),
    ("KI", _(u"Kiribati")),
    ("KP", _(u"Korea, Democratic People's Republic of")),
    ("KR", _(u"Korea, Republic of")),
    ("KW", _(u"Kuwait")),
    ("KG", _(u"Kyrgyzstan")),
    ("LA", _(u"Lao People's Democratic Republic")),
    ("LV", _(u"Latvia")),
    ("LB", _(u"Lebanon")),
    ("LS", _(u"Lesotho")),
    ("LR", _(u"Liberia")),
    ("LY", _(u"Libya")),
    ("LI", _(u"Liechtenstein")),
    ("LT", _(u"Lithuania")),
    ("LU", _(u"Luxembourg")),
    ("MO", _(u"Macao")),
    ("MK", _(u"Macedonia, The Former Yugoslav Republic of")),
    ("MG", _(u"Madagascar")),
    ("MW", _(u"Malawi")),
    ("MY", _(u"Malaysia")),
    ("MV", _(u"Maldives")),
    ("ML", _(u"Mali")),
    ("MT", _(u"Malta")),
    ("MH", _(u"Marshall Islands")),
    ("MQ", _(u"Martinique")),
    ("MR", _(u"Mauritania")),
    ("MU", _(u"Mauritius")),
    ("YT", _(u"Mayotte")),
    ("MX", _(u"Mexico")),
    ("FM", _(u"Micronesia, Federated States of")),
    ("MD", _(u"Moldova, Republic of")),
    ("MC", _(u"Monaco")),
    ("MN", _(u"Mongolia")),
    ("ME", _(u"Montenegro")),
    ("MS", _(u"Montserrat")),
    ("MA", _(u"Morocco")),
    ("MZ", _(u"Mozambique")),
    ("MM", _(u"Myanmar")),
    ("NA", _(u"Namibia")),
    ("NR", _(u"Nauru")),
    ("NP", _(u"Nepal")),
    ("NL", _(u"Netherlands")),
    ("NC", _(u"New Caledonia")),
    ("NZ", _(u"New Zealand")),
    ("NI", _(u"Nicaragua")),
    ("NE", _(u"Niger")),
    ("NG", _(u"Nigeria")),
    ("NU", _(u"Niue")),
    ("NF", _(u"Norfolk Island")),
    ("MP", _(u"Northern Mariana Islands")),
    ("NO", _(u"Norway")),
    ("OM", _(u"Oman")),
    ("PK", _(u"Pakistan")),
    ("PW", _(u"Palau")),
    ("PS", _(u"Palestinian Territory, Occupied")),
    ("PA", _(u"Panama")),
    ("PG", _(u"Papua New Guinea")),
    ("PY", _(u"Paraguay")),
    ("PE", _(u"Peru")),
    ("PH", _(u"Philippines")),
    ("PN", _(u"Pitcairn")),
    ("PL", _(u"Poland")),
    ("PT", _(u"Portugal")),
    ("PR", _(u"Puerto Rico")),
    ("QA", _(u"Qatar")),
    ("RE", _(u"Réunion")),
    ("RO", _(u"Romania")),
    ("RU", _(u"Russian Federation")),
    ("RW", _(u"Rwanda")),
    ("BL", _(u"Saint Barthélemy")),
    ("SH", _(u"Saint Helena, Ascension and Tristan Da Cunha")),
    ("KN", _(u"Saint Kitts and Nevis")),
    ("LC", _(u"Saint Lucia")),
    ("MF", _(u"Saint Martin (French Part)")),
    ("PM", _(u"Saint Pierre and Miquelon")),
    ("VC", _(u"Saint Vincent and the Grenadines")),
    ("WS", _(u"Samoa")),
    ("SM", _(u"San Marino")),
    ("ST", _(u"Sao Tome and Principe")),
    ("SA", _(u"Saudi Arabia")),
    ("SN", _(u"Senegal")),
    ("RS", _(u"Serbia")),
    ("SC", _(u"Seychelles")),
    ("SL", _(u"Sierra Leone")),
    ("SG", _(u"Singapore")),
    ("SX", _(u"Sint Maarten (Dutch Part)")),
    ("SK", _(u"Slovakia")),
    ("SI", _(u"Slovenia")),
    ("SB", _(u"Solomon Islands")),
    ("SO", _(u"Somalia")),
    ("ZA", _(u"South Africa")),
    ("GS", _(u"South Georgia and the South Sandwich Islands")),
    ("SS", _(u"South Sudan")),
    ("ES", _(u"Spain")),
    ("LK", _(u"Sri Lanka")),
    ("SD", _(u"Sudan")),
    ("SR", _(u"Suriname")),
    ("SJ", _(u"Svalbard and Jan Mayen")),
    ("SZ", _(u"Swaziland")),
    ("SE", _(u"Sweden")),
    ("CH", _(u"Switzerland")),
    ("SY", _(u"Syrian Arab Republic")),
    ("TW", _(u"Taiwan, Province of China")),
    ("TJ", _(u"Tajikistan")),
    ("TZ", _(u"Tanzania, United Republic of")),
    ("TH", _(u"Thailand")),
    ("TL", _(u"Timor-leste")),
    ("TG", _(u"Togo")),
    ("TK", _(u"Tokelau")),
    ("TO", _(u"Tonga")),
    ("TT", _(u"Trinidad and Tobago")),
    ("TN", _(u"Tunisia")),
    ("TR", _(u"Turkey")),
    ("TM", _(u"Turkmenistan")),
    ("TC", _(u"Turks and Caicos Islands")),
    ("TV", _(u"Tuvalu")),
    ("UG", _(u"Uganda")),
    ("UA", _(u"Ukraine")),
    ("AE", _(u"United Arab Emirates")),
    ("GB", _(u"United Kingdom")),
    ("US", _(u"United States")),
    ("UM", _(u"United States Minor Outlying Islands")),
    ("UY", _(u"Uruguay")),
    ("UZ", _(u"Uzbekistan")),
    ("VU", _(u"Vanuatu")),
    ("VE", _(u"Venezuela, Bolivarian Republic of")),
    ("VN", _(u"Viet Nam")),
    ("VG", _(u"Virgin Islands, British")),
    ("VI", _(u"Virgin Islands, U.S.")),
    ("WF", _(u"Wallis and Futuna")),
    ("EH", _(u"Western Sahara")),
    ("YE", _(u"Yemen")),
    ("ZM", _(u"Zambia")),
    ("ZW", _(u"Zimbabwe")),
)

READ_ONLY_IF_DATA_FIELDS = ["company", "full_name"]
DISABLED_IF_DATA_FIELDS = []

class UserNameInput(forms.TextInput):
    input_type = 'text'

    def __init__(self, attrs=None):
        if attrs is not None:
            self.input_type = attrs.pop('type', self.input_type)
        super(UserNameInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        final_attrs['value'] = force_text(self._format_value(value))
        return format_html('<input{0} />', flatatt(final_attrs))

class NoSuffixLabelForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(NoSuffixLabelForm, self).__init__(*args, **kwargs)

class LoginForm(NoSuffixLabelForm):
    ''' login form for system '''
    username = forms.CharField(max_length=255, label=mark_safe('Username <span class="required-field"></span>'))
    password = forms.CharField(widget=forms.PasswordInput(), label=mark_safe('Password <span class="required-field"></span>'))

class BaseRegistrationForm(NoSuffixLabelForm):
    ''' base for ActivationForm and FinalizeRegistrationForm '''
    email = forms.CharField(max_length=255, widget = forms.TextInput(attrs={'readonly':'readonly'}), label=mark_safe('Email'))
    username = forms.CharField(max_length=255, label=mark_safe('Public username <span class="tip">This cannot be changed later.</span> <span class="required-field"></span>'))
    password = forms.CharField(widget=forms.PasswordInput(),
        label=mark_safe('Password <span class="required-field"></span> <span class="tip">Must be at least 8 characters and include upper and lowercase letters - plus numbers OR special characters.</span> <span class="required-field"></span>'))
    company = forms.CharField(max_length=255, required=False)
    full_name = forms.CharField(max_length=512, required=False)
    title = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'required': True}), label=mark_safe('City <span class="required-field"></span>'))
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False)
    level_of_education = forms.ChoiceField(choices=EDUCATION_LEVEL_CHOICES, required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    year_of_birth = forms.ChoiceField(choices=YEAR_CHOICES, required=False, initial=("", "---"))
    accept_terms = forms.BooleanField(required=False, label=mark_safe('I agree to the <a href="/terms" target="_blank">Terms of Service</a> and <a href="/privacy" target="_blank">Privacy Policy</a> <span class="required-field"></span>'))

    def clean_accept_terms(self):
        value = self.cleaned_data['accept_terms']
        if not value:
            raise forms.ValidationError(_("You must accept terms of service in order to continue"))
        return value

class ActivationForm(BaseRegistrationForm):
    ''' activation form for system '''
    def __init__(self, *args, **kwargs):
        super(ActivationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = UserNameInput(attrs={'required': True})  # Custom widget with no default value
        if isinstance(args[0], dict):
            user_data = args[0]
            for read_only in READ_ONLY_IF_DATA_FIELDS:
                if read_only in user_data and user_data[read_only] is not None and len(user_data[read_only]) > 0:
                    self.fields[read_only].widget.attrs['readonly'] = 'readonly'

            for disabled in DISABLED_IF_DATA_FIELDS:
                if disabled in user_data and len(user_data[disabled]) > 0:
                    self.fields[disabled].widget.attrs['disabled'] = 'disabled'

class FinalizeRegistrationForm(BaseRegistrationForm):
    ''' activation form used to finalize a user's registration with SSO '''
    email = forms.EmailField(max_length=225, required=True, label=mark_safe('Email'))

    def __init__(self, user_data, fixed_values, **kwargs):
        initial = kwargs.pop('initial', {})
        initial.update(fixed_values)
        args = []
        if user_data is not None:
            # Don't allow users to change any fixed values,
            # but don't make this a bound form prematurely.
            user_data.update(fixed_values)
            args = [user_data]
        super(FinalizeRegistrationForm, self).__init__(*args, initial=initial, **kwargs)
        for field_name in fixed_values:
            self.fields[field_name].widget.attrs['readonly'] = 'readonly'
        self.fields.pop('password')  # No password required for SSO users

class FpasswordForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import EmailMessage

        email = self.cleaned_data["email"]

        users = user_api.get_users(email=email)
        if len(users) < 1:
            post_reset_redirect = '/accounts/login?reset=failed'
        else:
            user = users[0]

            uid = urlsafe_base64_encode(force_bytes(user.id))

            reset_record = UserPasswordReset.create_record(user)

            url = reverse('reset_confirm', kwargs={'uidb64':uid, 'token': reset_record.validation_key})

            c = {
                'email': user.email,
                'domain': request.META.get('HTTP_HOST'),
                'url': url,
                'user': user,
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            email = EmailMessage(subject, email, from_email, [user.email], headers = {'Reply-To': from_email})
            email.send(fail_silently=False)

class SetNewPasswordForm(forms.Form):
    """
    A form that lets a user change set his/her password without entering the
    old password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_validation': _("Password doesn't match creation criteria."),
    }
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetNewPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        try:
            response = user_api.update_user_information(self.user.id, {'password': self.cleaned_data['new_password1']})
        except ApiError as err:
            error = err.message
            self.user.error = error
            return self.user
        return self.user

class UploadProfileImageForm(forms.Form):
    ''' form to upload file for profile image '''
    profile_image = forms.FileField(label='', help_text="Formats accepted: JPG, PNG and GIF", required=False)

class EditFullNameForm(forms.Form):
    ''' edit user full name '''
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

class EditTitleForm(forms.Form):
    ''' edit user title '''
    title = forms.CharField(max_length=255, label='', required=False)

