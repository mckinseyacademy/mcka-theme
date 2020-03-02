#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' forms for login and activation '''
import datetime
import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.validators import validate_email, validate_slug
from django.core.exceptions import ValidationError

from api_client import user_api
from django.utils.html import format_html
from django.forms.utils import flatatt
from api_client.api_error import ApiError
from util.i18n_helpers import format_lazy, mark_safe_lazy

from .controller import send_password_reset_email
from .models import PublicRegistrationRequest
from admin.models import CourseRun, SelfRegistrationRoles, OTHER_ROLE
from util.validators import UsernameValidator, AlphanumericWithAccentedChars, RoleTitleValidator

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

YEAR_CHOICES = [("", "---"), ]
YEAR_CHOICES.extend(
    [
        (year_string, year_string) for year_string in [
            "{}".format(year_value) for year_value in reversed(
                list(range(datetime.date.today().year - 100, datetime.date.today().year - 10))
            )
        ]
    ]
)

COUNTRY_CHOICES = (
    ("", "---"),
    ("AF", _("Afghanistan")),
    ("AX", _("Åland Islands")),
    ("AL", _("Albania")),
    ("DZ", _("Algeria")),
    ("AS", _("American Samoa")),
    ("AD", _("Andorra")),
    ("AO", _("Angola")),
    ("AI", _("Anguilla")),
    ("AQ", _("Antarctica")),
    ("AG", _("Antigua and Barbuda")),
    ("AR", _("Argentina")),
    ("AM", _("Armenia")),
    ("AW", _("Aruba")),
    ("AU", _("Australia")),
    ("AT", _("Austria")),
    ("AZ", _("Azerbaijan")),
    ("BS", _("Bahamas")),
    ("BH", _("Bahrain")),
    ("BD", _("Bangladesh")),
    ("BB", _("Barbados")),
    ("BY", _("Belarus")),
    ("BE", _("Belgium")),
    ("BZ", _("Belize")),
    ("BJ", _("Benin")),
    ("BM", _("Bermuda")),
    ("BT", _("Bhutan")),
    ("BO", _("Bolivia, Plurinational State of")),
    ("BQ", _("Bonaire, Sint Eustatius and Saba")),
    ("BA", _("Bosnia and Herzegovina")),
    ("BW", _("Botswana")),
    ("BV", _("Bouvet Island")),
    ("BR", _("Brazil")),
    ("IO", _("British Indian Ocean Territory")),
    ("BN", _("Brunei Darussalam")),
    ("BG", _("Bulgaria")),
    ("BF", _("Burkina Faso")),
    ("BI", _("Burundi")),
    ("KH", _("Cambodia")),
    ("CM", _("Cameroon")),
    ("CA", _("Canada")),
    ("CV", _("Cape Verde")),
    ("KY", _("Cayman Islands")),
    ("CF", _("Central African Republic")),
    ("TD", _("Chad")),
    ("CL", _("Chile")),
    ("CN", _("China")),
    ("CX", _("Christmas Island")),
    ("CC", _("Cocos (Keeling) Islands")),
    ("CO", _("Colombia")),
    ("KM", _("Comoros")),
    ("CG", _("Congo")),
    ("CD", _("Congo, The Democratic Republic of the")),
    ("CK", _("Cook Islands")),
    ("CR", _("Costa Rica")),
    ("CI", _("Côte D'ivoire")),
    ("HR", _("Croatia")),
    ("CU", _("Cuba")),
    ("CW", _("Curaçao")),
    ("CY", _("Cyprus")),
    ("CZ", _("Czech Republic")),
    ("DK", _("Denmark")),
    ("DJ", _("Djibouti")),
    ("DM", _("Dominica")),
    ("DO", _("Dominican Republic")),
    ("EC", _("Ecuador")),
    ("EG", _("Egypt")),
    ("SV", _("El Salvador")),
    ("GQ", _("Equatorial Guinea")),
    ("ER", _("Eritrea")),
    ("EE", _("Estonia")),
    ("ET", _("Ethiopia")),
    ("FK", _("Falkland Islands (Malvinas)")),
    ("FO", _("Faroe Islands")),
    ("FJ", _("Fiji")),
    ("FI", _("Finland")),
    ("FR", _("France")),
    ("GF", _("French Guiana")),
    ("PF", _("French Polynesia")),
    ("TF", _("French Southern Territories")),
    ("GA", _("Gabon")),
    ("GM", _("Gambia")),
    ("GE", _("Georgia")),
    ("DE", _("Germany")),
    ("GH", _("Ghana")),
    ("GI", _("Gibraltar")),
    ("GR", _("Greece")),
    ("GL", _("Greenland")),
    ("GD", _("Grenada")),
    ("GP", _("Guadeloupe")),
    ("GU", _("Guam")),
    ("GT", _("Guatemala")),
    ("GG", _("Guernsey")),
    ("GN", _("Guinea")),
    ("GW", _("Guinea-bissau")),
    ("GY", _("Guyana")),
    ("HT", _("Haiti")),
    ("HM", _("Heard Island and McDonald Islands")),
    ("VA", _("Holy See (Vatican City State)")),
    ("HN", _("Honduras")),
    ("HK", _("Hong Kong")),
    ("HU", _("Hungary")),
    ("IS", _("Iceland")),
    ("IN", _("India")),
    ("ID", _("Indonesia")),
    ("IR", _("Iran, Islamic Republic of")),
    ("IQ", _("Iraq")),
    ("IE", _("Ireland")),
    ("IM", _("Isle of Man")),
    ("IL", _("Israel")),
    ("IT", _("Italy")),
    ("JM", _("Jamaica")),
    ("JP", _("Japan")),
    ("JE", _("Jersey")),
    ("JO", _("Jordan")),
    ("KZ", _("Kazakhstan")),
    ("KE", _("Kenya")),
    ("KI", _("Kiribati")),
    ("KP", _("Korea, Democratic People's Republic of")),
    ("KR", _("Korea, Republic of")),
    ("KW", _("Kuwait")),
    ("KG", _("Kyrgyzstan")),
    ("LA", _("Lao People's Democratic Republic")),
    ("LV", _("Latvia")),
    ("LB", _("Lebanon")),
    ("LS", _("Lesotho")),
    ("LR", _("Liberia")),
    ("LY", _("Libya")),
    ("LI", _("Liechtenstein")),
    ("LT", _("Lithuania")),
    ("LU", _("Luxembourg")),
    ("MO", _("Macao")),
    ("MK", _("Macedonia, The Former Yugoslav Republic of")),
    ("MG", _("Madagascar")),
    ("MW", _("Malawi")),
    ("MY", _("Malaysia")),
    ("MV", _("Maldives")),
    ("ML", _("Mali")),
    ("MT", _("Malta")),
    ("MH", _("Marshall Islands")),
    ("MQ", _("Martinique")),
    ("MR", _("Mauritania")),
    ("MU", _("Mauritius")),
    ("YT", _("Mayotte")),
    ("MX", _("Mexico")),
    ("FM", _("Micronesia, Federated States of")),
    ("MD", _("Moldova, Republic of")),
    ("MC", _("Monaco")),
    ("MN", _("Mongolia")),
    ("ME", _("Montenegro")),
    ("MS", _("Montserrat")),
    ("MA", _("Morocco")),
    ("MZ", _("Mozambique")),
    ("MM", _("Myanmar")),
    ("NA", _("Namibia")),
    ("NR", _("Nauru")),
    ("NP", _("Nepal")),
    ("NL", _("Netherlands")),
    ("NC", _("New Caledonia")),
    ("NZ", _("New Zealand")),
    ("NI", _("Nicaragua")),
    ("NE", _("Niger")),
    ("NG", _("Nigeria")),
    ("NU", _("Niue")),
    ("NF", _("Norfolk Island")),
    ("MP", _("Northern Mariana Islands")),
    ("NO", _("Norway")),
    ("OM", _("Oman")),
    ("PK", _("Pakistan")),
    ("PW", _("Palau")),
    ("PS", _("Palestinian Territory, Occupied")),
    ("PA", _("Panama")),
    ("PG", _("Papua New Guinea")),
    ("PY", _("Paraguay")),
    ("PE", _("Peru")),
    ("PH", _("Philippines")),
    ("PN", _("Pitcairn")),
    ("PL", _("Poland")),
    ("PT", _("Portugal")),
    ("PR", _("Puerto Rico")),
    ("QA", _("Qatar")),
    ("RE", _("Réunion")),
    ("RO", _("Romania")),
    ("RU", _("Russian Federation")),
    ("RW", _("Rwanda")),
    ("BL", _("Saint Barthélemy")),
    ("SH", _("Saint Helena, Ascension and Tristan Da Cunha")),
    ("KN", _("Saint Kitts and Nevis")),
    ("LC", _("Saint Lucia")),
    ("MF", _("Saint Martin (French Part)")),
    ("PM", _("Saint Pierre and Miquelon")),
    ("VC", _("Saint Vincent and the Grenadines")),
    ("WS", _("Samoa")),
    ("SM", _("San Marino")),
    ("ST", _("Sao Tome and Principe")),
    ("SA", _("Saudi Arabia")),
    ("SN", _("Senegal")),
    ("RS", _("Serbia")),
    ("SC", _("Seychelles")),
    ("SL", _("Sierra Leone")),
    ("SG", _("Singapore")),
    ("SX", _("Sint Maarten (Dutch Part)")),
    ("SK", _("Slovakia")),
    ("SI", _("Slovenia")),
    ("SB", _("Solomon Islands")),
    ("SO", _("Somalia")),
    ("ZA", _("South Africa")),
    ("GS", _("South Georgia and the South Sandwich Islands")),
    ("SS", _("South Sudan")),
    ("ES", _("Spain")),
    ("LK", _("Sri Lanka")),
    ("SD", _("Sudan")),
    ("SR", _("Suriname")),
    ("SJ", _("Svalbard and Jan Mayen")),
    ("SZ", _("Swaziland")),
    ("SE", _("Sweden")),
    ("CH", _("Switzerland")),
    ("SY", _("Syrian Arab Republic")),
    ("TW", _("Taiwan")),
    ("TJ", _("Tajikistan")),
    ("TZ", _("Tanzania, United Republic of")),
    ("TH", _("Thailand")),
    ("TL", _("Timor-leste")),
    ("TG", _("Togo")),
    ("TK", _("Tokelau")),
    ("TO", _("Tonga")),
    ("TT", _("Trinidad and Tobago")),
    ("TN", _("Tunisia")),
    ("TR", _("Turkey")),
    ("TM", _("Turkmenistan")),
    ("TC", _("Turks and Caicos Islands")),
    ("TV", _("Tuvalu")),
    ("UG", _("Uganda")),
    ("UA", _("Ukraine")),
    ("AE", _("United Arab Emirates")),
    ("GB", _("United Kingdom")),
    ("US", _("United States")),
    ("UM", _("United States Minor Outlying Islands")),
    ("UY", _("Uruguay")),
    ("UZ", _("Uzbekistan")),
    ("VU", _("Vanuatu")),
    ("VE", _("Venezuela, Bolivarian Republic of")),
    ("VN", _("Viet Nam")),
    ("VG", _("Virgin Islands, British")),
    ("VI", _("Virgin Islands, U.S.")),
    ("WF", _("Wallis and Futuna")),
    ("EH", _("Western Sahara")),
    ("YE", _("Yemen")),
    ("ZM", _("Zambia")),
    ("ZW", _("Zimbabwe")),
)

READ_ONLY_IF_DATA_FIELDS = ["company", "full_name"]
DISABLED_IF_DATA_FIELDS = []

BANNED_EMAILS = [
    "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
    "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
    "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
    "email.com", "games.com", "gmx.net", "hush.com", "hushmail.com", "icloud.com", "inbox.com",
    "lavabit.com", "love.com", "outlook.com", "pobox.com", "rocketmail.com",
    "safe-mail.net", "wow.com", "ygm.com", "ymail.com", "zoho.com", "fastmail.fm", "yandex.com",
    "bellsouth.net", "charter.net", "comcast.net", "cox.net", "earthlink.net", "juno.com",
    "btinternet.com", "virginmedia.com", "blueyonder.co.uk", "freeserve.co.uk", "live.co.uk",
    "ntlworld.com", "o2.co.uk", "orange.net", "sky.com", "talktalk.co.uk", "tiscali.co.uk",
    "sina.com", "qq.com", "naver.com", "hanmail.net", "daum.net", "nate.com", "yahoo.co.jp",
    "yahoo.co.kr", "yahoo.co.id", "yahoo.co.in", "yahoo.com.sg", "yahoo.com.ph",
    "hotmail.fr", "live.fr", "laposte.net", "yahoo.fr", "wanadoo.fr", "orange.fr", "gmx.fr",
    "sfr.fr", "neuf.fr", "free.fr", "virgin.net", "wanadoo.co.uk", "bt.com",
    "gmx.de", "hotmail.de", "live.de", "online.de", "t-online.de", "web.de", "yahoo.de",
    "mail.ru", "rambler.ru", "yandex.ru", "ya.ru", "list.ru", "hotmail.com.mx", "prodigy.net.mx", "msn.com",
    "hotmail.be", "live.be", "skynet.be", "voo.be", "tvcablenet.be", "telenet.be",
    "hotmail.com.ar", "live.com.ar", "yahoo.com.ar", "fibertel.com.ar", "speedy.com.ar", "arnet.com.ar",
    "hotmail.com", "gmail.com", "yahoo.com.mx", "live.com.mx", "yahoo.com", "hotmail.es", "live.com",
    "yahoo.com.br", "hotmail.com.br", "outlook.com.br", "uol.com.br", "bol.com.br", "terra.com.br",
    "ig.com.br", "itelefonica.com.br", "r7.com", "zipmail.com.br", "globo.com", "globomail.com", "oi.com.br",
    "accenture.com", "pwc.com", "deloitte.com", "bcg.com", "bain.com"
]


class UserNameInput(forms.TextInput):
    input_type = 'text'

    def __init__(self, attrs=None):
        if attrs is not None:
            self.input_type = attrs.pop('type', self.input_type)
        super(UserNameInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, extra_attrs={'type': self.input_type, 'name': name})
        final_attrs['value'] = ''
        return format_html('<input{0} />', flatatt(final_attrs))


class NoSuffixLabelForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(NoSuffixLabelForm, self).__init__(*args, **kwargs)


class SSOLoginForm(NoSuffixLabelForm):
    """ SSO dispatch form - asks user for email to look it up in a list of SSO-enabled accounts """
    # this is just used to differentiate this form from login form used on the same page
    sso_login_form_marker = forms.CharField(
        widget=forms.HiddenInput,
        required=False
    )
    email = forms.EmailField(
        max_length=255,
        label=mark_safe_lazy(format_lazy(
            _('Email address {html_span}'),
            html_span='<span class="required-field"></span>')
        ))


class LoginForm(NoSuffixLabelForm):
    ''' login form for system '''

    username = forms.CharField(
        max_length=255,
        label=mark_safe_lazy(format_lazy(
            _('Username {html_span}'),
            html_span='<span class="required-field"></span>')
        )
    )
    password = forms.CharField(widget=forms.PasswordInput(),
                               label=mark_safe_lazy(format_lazy(_('Password {html_span}'),
                                                                html_span='<span class="required-field"></span>'
                                                                )
                                                    )
                               )


class LoginIdForm(NoSuffixLabelForm):
    ''' login form for system '''

    login_id = forms.CharField(
        max_length=255,
        label=mark_safe_lazy(format_lazy(
            _('Username or Email {html_span}'),
            html_span='<span class="required-field"></span>')
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,  # This form can also be used to validate just the ID.
        label=mark_safe_lazy(format_lazy(
            _('Password {html_span}'),
            html_span='<span class="required-field"></span>')
        )
    )

    def clean_login_id(self):
        """
        Verifies a username/email is valid, raises a ValidationError otherwise.
        """
        cleaned_login_id = self.cleaned_data['login_id']
        try:
            if '@' in cleaned_login_id:
                validate_email(cleaned_login_id)
            else:
                validate_slug(cleaned_login_id)
        except ValidationError:
            if '@' in cleaned_login_id:
                raise forms.ValidationError(_("Please enter a valid email containing only English characters and"
                                              " numerals, and the following special characters @ . _ -"))
            else:
                raise forms.ValidationError(_("Please enter a valid username containing only English characters and "
                                              "numerals, and the following special characters _ - "))
        return cleaned_login_id


class AcceptTermsForm(NoSuffixLabelForm):
    accept_terms = forms.BooleanField(
        required=False,
        label=mark_safe_lazy(format_lazy(
            _('I agree to the {html_anchor_start} Terms of Service '
              '{html_anchor_end} and {html_anchor_second} Privacy Policy '
              '{html_anchor_end} {html_span}'),
            html_anchor_start='<a href="/terms" target="_blank">',
            html_anchor_end='</a>',
            html_anchor_second='<a href="/privacy" target="_blank">',
            html_span='<span class="required-field"></span>'
        ))
    )

    def clean_accept_terms(self):
        value = self.cleaned_data['accept_terms']
        if not value:
            raise forms.ValidationError(_("You must accept terms of service in order to continue"))
        return value


class AcceptTermsFormSSO(AcceptTermsForm):
    accept_terms = forms.BooleanField(
        required=True,
        label=mark_safe_lazy(format_lazy(
            _('I agree to the {html_anchor_start} Terms of Service '
              '{html_anchor_end} and {html_anchor_second} Privacy Policy '
              '{html_anchor_end} {html_span}'),
            html_anchor_start='<a href="/terms" target="_blank">',
            html_anchor_end='</a>',
            html_anchor_second='<a href="/privacy" target="_blank">',
            html_span='<span class="required-field"></span>'
        ))
    )


class BaseRegistrationForm(AcceptTermsForm):
    ''' base for ActivationForm and FinalizeRegistrationForm '''

    field_order = [
        'email', 'username', 'password', 'company', 'full_name',
        'title', 'city', 'country',
        # From AcceptTermsForm
        'accept_terms',
    ]

    email = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        label=_('Email')
    )

    username = forms.CharField(
        max_length=255,
        label=mark_safe_lazy(format_lazy(
            _('Public username {html_span_start} This cannot be changed later and '
              'cannot contain non-English characters.{html_span_end}'),
            html_span_start='<span class="tip">',
            html_span_end='</span> <span class="required-field"></span>'
        )),
        validators=[UsernameValidator()]
    )

    password = forms.CharField(
        widget=forms.PasswordInput(),
        label=mark_safe_lazy(format_lazy(
            _('Password {html_span_start} Must be at least 8 characters and include '
              'upper and lowercase letters - plus numbers OR special characters.{html_span_end}'),
            html_span_start='<span class="required-field"></span> <span class="tip">',
            html_span_end='</span> <span class="required-field"></span>'
            )
        )
    )

    company = forms.CharField(max_length=255, required=False, label=_("Company"))
    full_name = forms.CharField(max_length=512, required=False, label=_("Full Name"))
    title = forms.CharField(max_length=255, required=False, label=_("Title"), validators=[RoleTitleValidator()])
    city = forms.CharField(
        max_length=255, required=False, widget=forms.TextInput(attrs={'required': False}),
        label=mark_safe_lazy(format_lazy(
            _('City {html_span}'),
            html_span='<span class="required-field"></span>')),
        validators=[AlphanumericWithAccentedChars()]
    )
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, label=_("Country"), required=False)


class ActivationForm(BaseRegistrationForm):
    ''' activation form for system '''

    def __init__(self, *args, **kwargs):
        super(ActivationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = UserNameInput(attrs={'required': True})  # Custom widget with no default value
        if kwargs.get('initial'):
            initial_data = kwargs['initial']
            for read_only in READ_ONLY_IF_DATA_FIELDS:
                if read_only in initial_data and initial_data[read_only] is not None \
                        and len(initial_data[read_only]) > 0:
                    self.fields[read_only].widget.attrs['readonly'] = 'readonly'

            for disabled in DISABLED_IF_DATA_FIELDS:
                if disabled in initial_data and len(initial_data[disabled]) > 0:
                    self.fields[disabled].widget.attrs['disabled'] = 'disabled'


class FinalizeRegistrationForm(BaseRegistrationForm):
    ''' activation form used to finalize a user's registration with SSO '''
    email = forms.EmailField(max_length=225, required=True, label=mark_safe(_('Email')))

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

    def clean_email(self):
        email = self.cleaned_data["email"]
        users = user_api.get_users(fields=['is_active'], email=email)

        # only activated users can reset passwords
        if users and not (users[0].get('is_active')):
            raise ValidationError(
                _('The account associated with this email is not activated yet'),
                code='not_active'
            )

        return email

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.haml',
             email_template_name='registration/password_reset_email.haml',
             use_https=False, from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """

        email = self.cleaned_data["email"]

        users = user_api.get_users(email=email)
        if len(users) > 0:
            user = users[0]
            send_password_reset_email(
                request.META.get('HTTP_HOST'),
                user,
                use_https,
                subject_template_name=subject_template_name,
                email_template_name=email_template_name,
                from_email=from_email
            )


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
                                    widget=forms.PasswordInput(attrs={'class': "form-control form-input pswd1",
                                                                      'autocomplete': "off"}))
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput(attrs={'class': "form-control form-input pswd2",
                                                                      'autocomplete': "off"}))

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
            user_api.update_user_information(self.user.id, {'password': self.cleaned_data['new_password1']})
        except ApiError as err:
            error = err.message
            self.user.error = error
            return self.user
        return self.user


class UploadProfileImageForm(forms.Form):
    ''' form to upload file for profile image '''
    profile_image = forms.FileField(label='', help_text=_("Formats accepted: JPG, PNG and GIF"), required=False)


class EditFullNameForm(forms.Form):
    ''' edit user full name '''
    first_name = forms.CharField(
        max_length=30,
        label=_('First Name'),
        validators=[AlphanumericWithAccentedChars()],
        error_messages={"required": _("First Name is required.")}
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Last Name'),
        validators=[AlphanumericWithAccentedChars()],
        error_messages={"required": _("Last Name is required.")}
    )


class EditTitleForm(forms.Form):
    ''' edit user title '''
    title = forms.CharField(max_length=255, label='', required=False, validators=[AlphanumericWithAccentedChars()])


class BaseRegistrationFormV2(AcceptTermsForm):
    ''' base for ActivationForm and FinalizeRegistrationForm '''

    field_order = [
        'email', 'username', 'password', 'title', 'level_of_education',
        'year_of_birth',
        # From AcceptTermsForm
        'accept_terms',
    ]

    email = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                            label=mark_safe(_('Email')))
    username = forms.CharField(
        max_length=255,
        label=mark_safe_lazy(format_lazy(
            _('Public username {html_span_start} This cannot be changed later. {html_span_end}'),
            html_span_start='<span class="tip">',
            html_span_end='</span><span class="required-field"></span>'
        ))
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label=mark_safe_lazy(format_lazy(
            _('Password {html_span_start} Must be at least 8 characters and '
              'include upper and lowercase letters - plus numbers OR special '
              'characters.{html_span_end}'),
            html_span_start='<span class="required-field"></span> <span class="tip">',
            html_span_end='</span> <span class="required-field"></span>'
        ))
    )
    title = forms.CharField(max_length=255, required=False)
    level_of_education = forms.ChoiceField(choices=EDUCATION_LEVEL_CHOICES, required=False)
    year_of_birth = forms.ChoiceField(choices=YEAR_CHOICES, required=False, initial=("", "---"))


class ActivationFormV2(BaseRegistrationFormV2):
    ''' activation form for system '''
    def __init__(self, *args, **kwargs):
        super(ActivationFormV2, self).__init__(*args, **kwargs)
        self.fields['username'].widget = UserNameInput(attrs={'required': True})  # Custom widget with no default value


class PublicRegistrationForm(forms.ModelForm):
    current_role = forms.ModelChoiceField(widget=forms.RadioSelect,
                                          queryset=SelfRegistrationRoles.objects.all(), empty_label=None)
    current_role_other = forms.CharField(widget=forms.TextInput, label='', required=False)
    company_email = forms.CharField(max_length=70)

    class Meta:

        model = PublicRegistrationRequest
        fields = [
            'first_name',
            'last_name',
            'company_name',
            'company_email',
            'current_role',
            'current_role_other',
        ]

    def __init__(self, *args, **kwargs):
        self.course_run_name = kwargs.pop('course_run_name', None)
        super(PublicRegistrationForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].label = mark_safe_lazy(format_lazy(
            _('First Name {html_span}'),
            html_span='<span class="required-field"></span>'
        ))
        self.fields['last_name'].label = mark_safe_lazy(format_lazy(
            _('Last Name {html_span}'),
            html_span='<span class="required-field"></span>'
        ))
        self.fields['company_name'].label = mark_safe_lazy(format_lazy(
            _('Company Name {html_span}'),
            html_span='<span class="required-field"></span>'
        ))
        self.fields['company_email'].label = mark_safe_lazy(format_lazy(
            _('Company Email {html_span}'),
            html_span='<span class="required-field"></span>'
        ))
        self.fields['current_role'].label = mark_safe_lazy(format_lazy(
            _('Current Role {html_span}'),
            html_span='<span class="required-field"></span>'
        ))
        self.fields['company_email'].help_text = mark_safe_lazy(format_lazy(
            _('{html_div_start}Note: personal email addresses will not be processed{html_div_end}'),
            html_div_start='<div class="company_email_helptext">',
            html_div_end='</div>'
        ))

        self.fields['current_role'].help_text = mark_safe_lazy(format_lazy(
            _('{html_div_start}(please choose one of the following options) '
              '{html_div_end}'),
            html_div_start='<div class="current_role_helptext">',
            html_div_end='</div>'
        ))
        self.fields['current_role'].help_text = mark_safe_lazy(format_lazy(
            _('{html_div_start}(please choose one of the following options) '
              '{html_div_end}'),
            html_div_start='<div class="current_role_helptext">',
            html_div_end='</div>'
            )
        )

        self.fields['current_role_other'].widget.attrs.update({'maxlength': 60})
        choices = SelfRegistrationRoles.objects.filter(course_run__name=self.course_run_name)
        other_choice = choices.filter(option_text=OTHER_ROLE)
        roles_choice_list = [(choice.id, choice.option_text) for choice in choices
                             if choice.option_text.lower() != OTHER_ROLE.lower()]

        if other_choice:
            roles_choice_list = roles_choice_list + [(other_choice[0].id, other_choice[0].option_text)]
        self.fields['current_role'].choices = roles_choice_list

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        first_name = ' '.join(first_name.split())
        if not re.match(r'^[A-Za-z ]+$', first_name):
            raise forms.ValidationError(_("Special characters or numbers are not valid."))
        else:
            return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        last_name = ' '.join(last_name.split())
        if not re.match(r'^[A-Za-z ]+$', last_name):
            raise forms.ValidationError(_("Special characters or numbers are not valid."))
        else:
            return last_name

    def clean_company_email(self):

        company_email = self.cleaned_data.get("company_email")

        if not isinstance(company_email, str):
            raise forms.ValidationError(_("Email must be a string."))

        if len(company_email) < 3:
            raise forms.ValidationError(
                format_lazy(
                    _("Email '{email}' must be at least {min} characters long"),
                    email=company_email,
                    min=3)
            )

        if len(company_email) > 70:
            raise forms.ValidationError(format_lazy(
                                                    _("Email '{email}' must be at most {max} characters long"),
                                                    email=company_email,
                                                    max=70
                                                    )
                                        )

        course_run = CourseRun.objects.filter(name=self.course_run_name)
        users = PublicRegistrationRequest.objects.filter(course_run__in=course_run)
        for user in users:
            if user.company_email == company_email:
                raise forms.ValidationError(_("This email address has already been registered."))

        try:
            validate_email(company_email)
            company_domain = company_email.split('@')[1].lower()
            if company_domain in BANNED_EMAILS:
                raise forms.ValidationError(_("Email you provided is not allowed."))
        except Exception:  # pylint: disable=bare-except TODO: add specific Exception class
            raise forms.ValidationError(_("Please enter a valid company email address."))

        course_run = CourseRun.objects.filter(name=self.course_run_name)

        user_emails = PublicRegistrationRequest.objects.filter(
            course_run__in=course_run).values_list('company_email', flat=True)

        if company_email.lower in user_emails:
                raise forms.ValidationError("This email address has already been registered.")

        return company_email

    def clean_company_name(self):

        company_name = self.cleaned_data.get("company_name")
        company_name = ' '.join(company_name.split())

        if not re.match(r'^[A-Za-z0-9 ]+$', company_name):
            raise forms.ValidationError(_("Special characters are not valid."))

        return company_name

    def clean_current_role_other(self):

        current_role = self.cleaned_data.get("current_role")
        if current_role:
            current_role = current_role.option_text

        current_role_other = self.cleaned_data.get("current_role_other")

        current_role_other = ' '.join(current_role_other.split())

        if OTHER_ROLE == current_role and not current_role_other:
            raise forms.ValidationError("Please specify your Role.")

        if OTHER_ROLE == current_role:
            if not re.match(r'^[A-Za-z0-9 ]+$', current_role_other):
                raise forms.ValidationError(_("Please enter a valid Role."))

        return current_role_other
