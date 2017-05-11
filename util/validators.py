# -*- coding: utf-8 -*-

""" validation utils """

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from .data_sanitizing import remove_diacritics


class UsernameValidator(RegexValidator):
    """
    Allows letters, numbers, underscores and hyphens in accordance with
    the username validation used at EdX platform API
    """
    regex = r'^[a-zA-Z0-9_-]+\Z'
    message = _("Username can only consist of letters, numbers underscores and hyphens, with no spaces.")


class AlphanumericValidator(RegexValidator):
    """
    Validates that given value is alphanumeric characters with hyphens,
    dots, underscore and spaces
    """
    regex = r'^[a-zA-Z0-9-_\. ]+\Z'
    message = _("Enter a valid value consisting of letters, numbers, underscores, dots, hyphens or spaces.")


class AlphanumericWithAccentedChars(AlphanumericValidator):
    """
    Extends AlphanumericValidator to include accented characters
    """
    def __call__(self, value):
        value = remove_diacritics(value)
        super(AlphanumericWithAccentedChars, self).__call__(value)


def validate_first_name(first_name):
    """
    Validates Participant first name according to first name validation rules

    Raises:
         ValidationError: if validation fails
    """
    message = _('First name: {}'.format(AlphanumericWithAccentedChars.message))
    validator = AlphanumericWithAccentedChars(message=message)

    validator(first_name)


def validate_last_name(last_name):
    """
    Validates Participant last name according to last name validation rules

    Raises:
         ValidationError: if validation fails
    """
    message = _('Last name: {}'.format(AlphanumericWithAccentedChars.message))
    validator = AlphanumericWithAccentedChars(message=message)

    validator(last_name)
