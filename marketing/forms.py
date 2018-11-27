#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' forms for public marketing pages '''
from django import forms
from django.utils.translation import ugettext as _
from django.conf import settings

import urllib2 as url_access
from urllib2 import HTTPError
import base64
import json

TIMEOUT = 20

TECH_SUPPORT_CHOICES = (
    ("", _("Please Select")),
    ("problem", _("Technical Issue")),
    ("incident", _("Course Issue")),
    ("question", _("Question")),
    ("task", _("Suggestion")),
)

EDUCATION_CHOICES = (
    ("", _("Please Select")),
    ("Bachelor's degree", _("Bachelor's degree")),
    ("mba", _("Master's of Business Administration (MBA)")),
    ("Master's degree", _("Master's degree (non MBA)")),
    ("PHD", _("Doctorate (PhD)")),
    ("other", _("Other")),
)

USER_TOKEN = '{}/token:{}'.format(
    settings.ZENDESK_API['username'],
    settings.ZENDESK_API['token'],
)

USER_AUTH = base64.encodestring(USER_TOKEN).replace('\n', '')


class TechSupportForm(forms.Form):
    auto_id = False
    type = forms.ChoiceField(label=False, choices=TECH_SUPPORT_CHOICES)
    name = forms.CharField(label=False, max_length=254, widget=forms.TextInput(
        attrs={'placeholder': _('Name')}))
    email = forms.EmailField(label=False, max_length=254, widget=forms.TextInput(
        attrs={'placeholder': _('Email')}))
    comment = forms.CharField(label=False, widget=forms.widgets.Textarea(
        attrs={'placeholder': _('Please provide details')})
                              )
    device = forms.CharField(widget=forms.HiddenInput(), required=False)
    device_language = forms.CharField(widget=forms.HiddenInput(), required=False)
    browser_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    browser_version = forms.CharField(widget=forms.HiddenInput(), required=False)
    user_agent = forms.CharField(widget=forms.HiddenInput(), required=False)

    def save(self):
        data = {
            'ticket': {
                'type': self.cleaned_data['type'],
                'requester': {
                    'name': self.cleaned_data['name'],
                    'email': self.cleaned_data['email'],
                },
                'comment': {
                    'body': self.cleaned_data['comment']
                },
                'custom_fields': [
                    {22628294: self.cleaned_data['email']},
                    {22628304: self.cleaned_data['device']},
                    {22628314: self.cleaned_data['device_language']},
                    {22790330: self.cleaned_data['browser_type']},
                    {22790340: self.cleaned_data['browser_version']},
                    {22628334: self.cleaned_data['user_agent']},
                ]
            }
        }

        tickets_url = 'https://{}.zendesk.com/api/v2/tickets.json'.format(
            settings.ZENDESK_API['subdomain']
        )

        url_request = url_access.Request(url=tickets_url)
        url_request.add_header("Authorization", "Basic %s" % USER_AUTH)
        url_request.add_header("Content-Type", "application/json")
        url_access.urlopen(url_request, json.dumps(data), TIMEOUT)


class SubscribeForm(forms.Form):
    auto_id = False
    email = forms.EmailField(label=False, max_length=254, widget=forms.TextInput(
        attrs={
            'placeholder': _('Email')
        }
    ))

    def save(self):
        data = {
            'apikey': settings.MAILCHIMP_API['key'],
            'id': settings.MAILCHIMP_API['stay_informed_list_id'],
            'email': {
                'email': self.cleaned_data['email'],
            },
        }

        subscribe_url = 'https://{}.api.mailchimp.com/2.0/lists/subscribe.json'.format(
            settings.MAILCHIMP_API['dc']
        )

        url_request = url_access.Request(url=subscribe_url)
        url_request.add_header("Content-Type", "application/json")
        try:
            url_access.urlopen(url_request, json.dumps(data), TIMEOUT)
        except HTTPError:
            return False


class EdxOfferForm(forms.Form):
    auto_id = False
    full_name = forms.CharField(label=False, max_length=254, widget=forms.TextInput(
        attrs={
            'placeholder': _('Full name'),
            'required': None,
            'data-entry': 'entry.867370117'
        }
    ))

    # TODO: handle invalid escape sequence
    email = forms.EmailField(label=False, max_length=254, widget=forms.TextInput(  # noqa: W605
        attrs={
            'type': 'email',
            'placeholder': _('Email'),
            'required': '',
            'pattern': '^[\w\d_.%+-]+@[\w\d.-]+\.[a-z]{2,6}$',
            'data-entry': 'entry.161345890'
        }
    ))

    company = forms.CharField(label=False, max_length=254, widget=forms.TextInput(
        attrs={
            'placeholder': _('Company'),
            'required': None,
            'data-entry': 'entry.925379726'
        }
    ))

    title = forms.CharField(label=False, max_length=254, widget=forms.TextInput(
        attrs={
            'placeholder': _('Title'),
            'required': None, 'data-entry': 'entry.143346488'
        }
    ))
    education = forms.ChoiceField(
        label=_('Highest level of education completed:'),
        choices=EDUCATION_CHOICES,
        widget=forms.Select(attrs={'data-entry': 'entry.24647299'})
    )

    comment = forms.CharField(
        label=False,
        widget=forms.widgets.Textarea(
            attrs={
                'placeholder': _('In a few lines tell us why you would like to take the course.'),
                'required': None,
                'data-entry': 'entry.1495472333'
            }
        )
    )
