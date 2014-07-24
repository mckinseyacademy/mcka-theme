''' A set of generic utilities '''

class DottableDict(dict):
    ''' The usual hack for accessing dict keys via dot notation,
        as in my_dict.key instead of my_dict['key'] '''
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

class LegacyIdConvert(object):

    @staticmethod
    def _slashes(slash_string):
        course_id_components = slash_string.split('+')
        return '/'.join(course_id_components)

    @staticmethod
    def _location(location_string):
        module_components = location_string.split('+')
        # remove the 3rd component (course run) - this is ignored
        old_path_components = ["i4x:/"]
        old_path_components.extend(module_components[:2])
        old_path_components.extend(module_components[3:])
        return '/'.join(old_path_components)

    @staticmethod
    def _slashify(slashed_string):
        return "slashes:{}".format('+'.join(slashed_string.split('/')))

    @staticmethod
    def _locationify(slashed_string, course_key):
        location_components = course_key.split('/')
        # remove original course components, and put full course components back in place
        location_components.extend(slashed_string.strip('/').split('/')[2:])
        return "location:{}".format('+'.join(location_components))

    @staticmethod
    def legacy_from_new(new_format_key):
        ''' any problems, assume that it has already been translated somewhere else '''
        try:
            split_head = new_format_key.split(':')
            if len(split_head) != 2:
                raise Exception("Unsupported new key format")

            translator = getattr(LegacyIdConvert, "_" + split_head[0], None)
            if translator is None:
                raise Exception("Unsupported new key format")

            return translator(split_head[1])
        except:
            print "Error translating key - assuming already in old format for {}".format(new_format_key)
            return new_format_key

    @staticmethod
    def new_from_legacy(old_format_key, course_key = None):
        try:
            split_head = old_format_key.split(':')
            if len(split_head) < 2:
                return LegacyIdConvert._slashify(split_head[0])
            else:
                if split_head[0] not in ["i4x"]:
                    raise Exception("Unsupported old key format")
                return LegacyIdConvert._locationify(
                    split_head[1],
                    course_key
                )
        except:
            print "Error translating key - assuming already in new format for {}".format(old_format_key)
            return old_format_key
