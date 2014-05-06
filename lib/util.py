''' A set of generic utilities '''

class DottableDict(dict):
    ''' The usual hack for accessing dict keys via dot notation, 
        as in my_dict.key instead of my_dict['key'] '''
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self