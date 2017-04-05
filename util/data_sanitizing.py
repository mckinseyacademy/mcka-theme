""" generic data clean utilities """

import logging

from django.conf import settings
from django.utils.html import escape
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

_logger = logging.getLogger(__name__)


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


def remove_characters(value, char_blacklist):
    """
    Remove blacklist characters from the value
    """
    remove_chars_map = dict((ord(char), None) for char in char_blacklist)

    # encode strings to unicode for consistency
    value = value if isinstance(value, unicode) else unicode(value)

    return value.translate(remove_chars_map)


def clean_formula_characters(value):
    """
    Remove formula injection characters from passed string
    """
    return remove_characters(value, settings.CSV_CHARACTERS_BLACKLIST)


def clean_xss_characters(value):
    """
    Remove XSS related characters from passed string
    """
    return escape(value)


def apply_clean_methods(value, methods=()):
    """
    Pass `value` through clean methods
    """
    methods = methods or DEFAULT_CLEAN_METHODS

    for method in methods:
        # don't break if a method fails
        try:
            value = method(value)
        except Exception as e:
            _logger.warning('Clean method `{}` failed with message "{}"'.format(method.__name__, e.message))

    return value


def sanitize_data(data, props_to_clean=None, additional_clean_methods=()):
    """
    Sanitize data using default and additional passed clean methods
    default clean methods sanitize data for:
        csv formula injection characters
        xss characters

    Args:
        data: data dict, keys are interpreted as properties
        props_to_clean: list of keys to apply clean on, if not supplied all data is cleaned
        additional_clean_methods: tuple of methods to apply on each value along with default cleaning
    Returns:
        dict with cleaned data
    Raises:
        TypeError: if data is not a dictionary
        TypeError: if additional_clean_methods is not a tuple
        TypeError: if any one of additional methods is not a callable
    """
    if not isinstance(data, dict):
        raise TypeError('data must be a dictionary')

    if not isinstance(additional_clean_methods, tuple):
        raise TypeError('additional_clean_methods must be a tuple of methods')

    if not all((callable(method) for method in additional_clean_methods)):
        raise TypeError('one of the additional methods is not a callable')

    clean_methods = DEFAULT_CLEAN_METHODS + additional_clean_methods

    for key, val in data.items():
        if (not props_to_clean) or (key in props_to_clean):
            data[key] = apply_clean_methods(val, clean_methods)

    return data


DEFAULT_CLEAN_METHODS = (clean_formula_characters, clean_xss_characters)
