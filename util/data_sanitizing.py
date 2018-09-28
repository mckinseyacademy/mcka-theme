# -*- coding: utf-8 -*-

""" generic data clean utilities """

import logging
import unicodedata
import re

from django.conf import settings
from django.utils.html import escape


_logger = logging.getLogger(__name__)


def remove_diacritics(text):
    """
    Return a string with all diacritics (aka non-spacing marks) removed

    For example "Héllô" will become "Hello"
    Useful for comparing strings in an accent-insensitive fashion
    """
    text = text if isinstance(text, unicode) else unicode(text, encoding='utf-8')

    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def remove_characters(value, char_blacklist):
    """
    Remove blacklist characters from the value
    """
    remove_chars_map = dict((ord(char), None) for char in char_blacklist)

    # encode strings to unicode for consistency
    value = value if isinstance(value, unicode) else unicode(value, encoding='utf-8')

    return value.translate(remove_chars_map)


def prepend_formula_value(value):
    """
    Prepends apostrophe to value if it contains formula injection characters
    """
    if any(char in value for char in settings.CSV_CHARACTERS_BLACKLIST):
        value = "'{}".format(value)

    return value


def clean_formula_characters(value):
    """
    Remove or prepend formula injection characters
    """
    if settings.FORMULA_CLEAN_STRATEGY == 'remove':
        return remove_characters(value, settings.CSV_CHARACTERS_BLACKLIST)
    elif settings.FORMULA_CLEAN_STRATEGY == 'prepend':
        return prepend_formula_value(value)


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


def sanitize_data(data, props_to_clean=None, clean_methods=()):
    """
    Sanitize data using default and passed clean methods
    default clean methods sanitize data for:
        csv formula injection characters
        xss characters

    Args:
        data: data dict, keys are interpreted as properties
        props_to_clean: list of keys to apply clean on, if not supplied all data is cleaned
       clean_methods: tuple of methods to apply on each value
    Returns:
        dict with cleaned data
    Raises:
        TypeError: if data is not a dictionary
        TypeError: if clean_methods is not a tuple
        TypeError: if any one of clean methods is not a callable
    """
    if not isinstance(data, dict):
        raise TypeError('data must be a dictionary')

    if not isinstance(clean_methods, tuple):
        raise TypeError('clean_methods must be a tuple of methods')

    if not all((callable(method) for method in clean_methods)):
        raise TypeError('one of the additional methods is not a callable')

    clean_methods = clean_methods or DEFAULT_CLEAN_METHODS

    for key, val in data.items():
        if (not props_to_clean) or (key in props_to_clean):
            data[key] = apply_clean_methods(val, clean_methods)

    return data


DEFAULT_CLEAN_METHODS = (clean_xss_characters, clean_formula_characters, )


def special_characters_match(value):
    """
    This method will return special character if there are any in string.
    """

    return re.sub(settings.FOREIGN_AND_NORMAL_CHARACTERS_PATTERN, u'', value.encode('utf-8').decode('latin_1'))

