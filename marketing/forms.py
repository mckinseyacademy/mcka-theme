#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' forms for public marketing pages '''
import datetime
from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings

import urllib2 as url_access
import base64
import json

TIMEOUT = 20

TECH_SUPPORT_CHOICES = (
    ("", "Please Select…"),
    ("problem", _("Site Issue")),
    ("incident", _("Course Issue")),
    ("incident", _("Lesson Issue")),
)

USER_TOKEN = '{}/token:{}'.format(
    settings.ZENDESK_API['username'],
    settings.ZENDESK_API['token'],
)

USER_AUTH = base64.encodestring(USER_TOKEN).replace('\n', '')

class TechSupportForm(forms.Form):
    auto_id = False
    type = forms.ChoiceField(label=False, choices=TECH_SUPPORT_CHOICES)
    name = forms.CharField(label=False, max_length=254, widget=forms.TextInput(attrs={'placeholder': _('Name')}))
    email = forms.EmailField(label=False, max_length=254, widget=forms.TextInput(attrs={'placeholder': _('Email')}))
    comment = forms.CharField(label=False, widget=forms.widgets.Textarea(attrs={'placeholder': _('Please provide details')}))
    device = forms.CharField(widget=forms.HiddenInput())
    device_language = forms.CharField(widget=forms.HiddenInput())
    browser_type = forms.CharField(widget=forms.HiddenInput())
    browser_version = forms.CharField(widget=forms.HiddenInput())
    user_agent = forms.CharField(widget=forms.HiddenInput())

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
