''' A set of generic utilities '''
import os


class DottableDict(dict):
    ''' The usual hack for accessing dict keys via dot notation,
        as in my_dict.key instead of my_dict['key'] '''
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self


class PriorIdConvert(object):

    @staticmethod
    def _slashes(slash_string):
        course_id_components = slash_string.split('+')
        return '/'.join(course_id_components)

    @staticmethod
    def _location(location_string):
        module_components = location_string.split('+')
        # remove the 3rd component (course run) - this is ignored
        new_path_components = ["i4x:/"]
        new_path_components.extend(module_components[:2])
        new_path_components.extend(module_components[3:])
        return '/'.join(new_path_components)

    @staticmethod
    def new_from_prior(prior_format_key):
        ''' any problems, assume that it has already been translated somewhere else '''
        try:
            split_head = prior_format_key.split(':')
            if len(split_head) != 2:
                raise Exception("Unsupported prior key format")

            translator = getattr(PriorIdConvert, "_" + split_head[0], None)
            if translator is None:
                raise Exception("Unsupported prior key format")

            return translator(split_head[1])
        except:
            print "Error translating key - assuming already in new format for {}".format(prior_format_key)
            return prior_format_key


def find_maxmind_database():
    """
    Attempts to find the path to the Maxmind database.

    :exception IOError: An IOError will occur if path cannot be found.

    :return: Returns the path to the database.
    """
    lib_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(lib_directory, 'GeoLite2-Country.mmdb'))
    if not os.path.exists(file_path):
        raise IOError('Maxmind database not found in {0}.'.format(file_path))
    return file_path


def get_client_ip_address(request):
    """
    Gets the client's IP Address from the provided request.
    :param request: The client's request.
    :return: Returns the IP Address Example: '8.8.8.8'
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
