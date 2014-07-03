#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' forms for login and activation '''
import datetime
from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from lib.token_generator import ResetPasswordTokenGenerator

from api_client import user_api
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.urlresolvers import reverse
from api_client.api_error import ApiError


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
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False)
    level_of_education = forms.ChoiceField(choices=EDUCATION_LEVEL_CHOICES, required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    year_of_birth = forms.ChoiceField(choices=YEAR_CHOICES, required=False, initial=("", "---"))
    accept_terms = forms.BooleanField(required=False, label=mark_safe('I agree to the <a href="/terms" target="_blank">Terms of Service</a> and <a href="/privacy" target="_blank">Privacy Policy</a> <span class="required-field"></span>'))
    #accept_terms = forms.CheckboxInput()

    def __init__(self, *args, **kwargs):
        super(ActivationForm, self).__init__(*args, **kwargs)
        if isinstance(args[0], dict):
            user_data = args[0]
            for read_only in READ_ONLY_IF_DATA_FIELDS:
                if read_only in user_data and len(user_data[read_only]) > 0:
                    self.fields[read_only].widget.attrs['readonly'] = 'readonly'

            for disabled in DISABLED_IF_DATA_FIELDS:
                if disabled in user_data and len(user_data[disabled]) > 0:
                    self.fields[disabled].widget.attrs['disabled'] = 'disabled'


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

class FpasswordForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=ResetPasswordTokenGenerator(),
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import EmailMessage

        email = self.cleaned_data["email"]

        users = user_api.get_users([{'key': 'email', 'value': email}])
        if users.count < 1:
            post_reset_redirect = '/accounts/login?reset=failed'
        else:
            user = users.results[0]
            token_generator = ResetPasswordTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))

            url = reverse('reset_confirm', kwargs={'uidb64':uid, 'token': token})

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
            if err.code == 400:
                error = err.message
                self.user.error = error
                return self.user
        return self.user


class UploadProfileImageForm(forms.Form):

    ''' form to upload file for profile image '''
    profile_image = forms.FileField(label='Select new profile image', help_text="Use JPG images. Example: profile_image.jpg", required=False)
