""" generic data clean functions """

from copy import deepcopy

from django.conf import settings


def sanitize_data(data, props_to_clean=None, char_blacklist=None):
    """
    Apply clean methods on supplied data

    Args:
        data: data dict, keys are interpreted as properties
        props_to_clean: list of keys to apply clean on, if not supplied all data is cleaned
        char_blacklist: list of characters to remove from data
    Returns:
        dict with cleaned data
    Raises:
        TypeError if data is not a dictionary
    """
    if not isinstance(data, dict):
        raise TypeError('data must be a dictionary')

    char_blacklist = char_blacklist or settings.CSV_CHARACTERS_BLACKLIST

    cleaned_data = deepcopy(data)

    for key, val in cleaned_data.items():
        if props_to_clean:
            if key in props_to_clean:
                cleaned_data[key] = remove_characters(val, char_blacklist)
        else:
            cleaned_data[key] = remove_characters(val, char_blacklist)

    return cleaned_data


def remove_characters(value, char_blacklist):
    """
    Remove blacklist characters from the value
    """
    remove_chars_map = dict((ord(char), None) for char in char_blacklist)

    # encode strings to unicode for consistency
    value = value if isinstance(value, unicode) else unicode(value)

    return value.translate(remove_chars_map)
