""" CSV clean functions """

from django.conf import settings


CHAR_BLACKLIST = ''.join(settings.CSV_CHARACTERS_BLACKLIST)


def sanitize(col_val):
    san_val = remove_characters(col_val, CHAR_BLACKLIST)
    return san_val


def remove_characters(passed_value, CHAR_BLACKLIST):
    return passed_value.translate(None,CHAR_BLACKLIST)
