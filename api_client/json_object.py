''' Base classes to read json responses into objects '''
import json
import collections

# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods

class Objectifier(object):

    '''
    Class to build class-instance accessors from provided dictionary object
    '''
    object_map = {}

    @classmethod
    def objectify_if_iterable(cls, value):
        ''' Create an array of objects of this type if value is an array '''
        if isinstance(value, collections.Iterable):
            return cls(dictionary=value)
        else:
            return value

    def __init__(self, dictionary):
        self._build_from_dictionary(dictionary)

    def _build_from_dictionary(self, dictionary):
        ''' Construct the attributes of the object from the given dictionary '''
        for item in dictionary:
            object_type = self._object_type_for_name(item)

            if isinstance(dictionary[item], dict):
                self.__setattr__(
                    item,
                    object_type(dictionary=dictionary[item])
                )
            elif isinstance(dictionary[item], list):
                self.__setattr__(
                    item,
                    map(object_type.objectify_if_iterable, dictionary[item])
                )
            else:
                self.__setattr__(item, dictionary[item])

    def _object_type_for_name(self, item_name):
        '''
        Configure object types in child classes; used when we desire a
        child object for an attribute instead of default Objectifier object
        '''
        object_type = Objectifier
        if item_name in self.object_map:
            object_type = self.object_map[item_name]

        return object_type


class MissingRequiredFieldError(Exception):

    '''
    Exception to be thrown when a required field is missing
    '''

    def __init__(self, value):
        self.value = value
        super(MissingRequiredFieldError, self).__init__()

    def __str__(self):
        return "Missing required field '{}'".format(self.value)


# Can create one of these, and add some class-specific checks for required
# values, even strip bad values
class JsonObject(Objectifier):

    '''
    Create an python object from a json object
    Can inherit from this class if you like, specifying member overrides
        required_fields - list of field names that must be present to
            instantiate this object
        valid_fields - list of fields that are expected; define this if you
            want to strip unexpected fields from the generate object
    Alternatively, just instantiate one of these from a dictionary object
        instead of json
    '''
    required_fields = []
    valid_fields = None

    def __init__(self, json_data=None, dictionary=None):
        if dictionary == None and json_data != None:
            dictionary = json.loads(json_data)

        if dictionary != None:
            self._validate_fields(dictionary)
            super(JsonObject, self).__init__(dictionary)
            # self._build_from_dictionary(dictionary)

    def _validate_fields(self, dictionary):
        '''
        Ensures that generated class has required_fields and,
        if specified, that only valid_fields remain
        '''
        for required in self.required_fields:
            if not required in dictionary:
                raise MissingRequiredFieldError(required)
        if self.valid_fields:
            remove_fields = []
            for element in dictionary:
                if not element in self.valid_fields:
                    remove_fields.append(element)
            for remove_field in remove_fields:
                del dictionary[remove_field]


class JsonParser(object):

    '''
    JsonParser static class to initiate parsing of json into specific
    JsonObject impementations
    '''
    @staticmethod
    def from_json(json_data, object_type=JsonObject):
        ''' takes json => dictionary / array and processes it accordingly '''
        parsed_json = json.loads(json_data)
        if isinstance(parsed_json, list):
            out_objects = []
            for json_dictionary in parsed_json:
                out_objects.append(object_type(dictionary=json_dictionary))

            return out_objects
        else:
            return object_type(json_data)
