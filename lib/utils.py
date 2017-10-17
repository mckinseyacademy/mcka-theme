''' A set of generic utilities '''


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
