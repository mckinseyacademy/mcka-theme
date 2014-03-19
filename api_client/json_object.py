import json
import collections


class Objectifier(object):

    '''
    Class to build class-instance accessors from provided dictionary object
    '''
    object_map = {}

    @staticmethod
    def _objectify_if_iterable(value, object_type = None):
        if isinstance(value, collections.Iterable):
            if object_type == None:
                object_type = Objectifier

            return object_type(dictionary=value)
        else:
            return value

    def __init__(self, dictionary):
        self._build_from_dictionary(dictionary)

    def _build_from_dictionary(self, dictionary):
        for item in dictionary:
            object_type = self._object_type_for_name(item)

            if isinstance(dictionary[item], dict):
                self.__setattr__(item, object_type(dictionary=dictionary[item]))
            elif isinstance(dictionary[item], list):
                self.__setattr__(item, map(object_type._objectify_if_iterable, dictionary[item]))
            else:
                self.__setattr__(item, dictionary[item])

    def _object_type_for_name(self, item_name):
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

    def __str__(self):
        return "Missing required field '{}'".format(self.value)


# Can create one of these, and add some class-specific checks for required
# values, even strip bad values
class JsonObject(Objectifier):

    '''
    Create an python object from a json object
    Can inherit from this class if you like, specifying member overrides
        required_fields - list of field names that must be present to instantiate this object
        valid_fields - list of fields that are expected; define this if you want to strip unexpected fields from the generate object
    Alternatively, just instantiate one of these from a 
    '''
    required_fields = []
    valid_fields = None

    def __init__(self, json_data=None, dictionary=None):
        if(dictionary == None and json_data != None):
            dictionary = json.loads(json_data)

        if(dictionary != None):
            self._validate_fields(dictionary)
            self._build_from_dictionary(dictionary)

    def _validate_fields(self, dictionary):
        for required in self.required_fields:
            if not (required in dictionary):
                raise MissingRequiredFieldError(required)
        if self.valid_fields:
            remove_fields = []
            for element in dictionary:
                if not (element in self.valid_fields):
                    remove_fields.append(element)
            for remove_field in remove_fields:
                del dictionary[remove_field]


class JsonParser:

    @staticmethod
    def from_json(json_data, object_type=JsonObject):
        parsed_json = json.loads(json_data)
        if isinstance(parsed_json, list):
            out_objects = []
            for jo in parsed_json:
                out_objects.append(object_type(dictionary=jo))

            return out_objects
        else:
            return object_type(json_data)


if __name__ == "__main__":
    # Some test objects for the above
    class Pupil(JsonObject):
        required_fields = ['name', 'age']

    class StrictPupil(JsonObject):
        required_fields = ['name', 'age']
        valid_fields = ['name', 'age', 'children']

    pupil1 = '{"name":"Martyn", "age":21}'
    pupil2 = '{"name":"Martyn"}'
    pupil3 = '{"age":21}'
    pupil4 = '{"name":"Martyn", "age":21, "children":4, "wife":"Monica"}'

    pupils = '[{},{}]'.format(pupil1, pupil4)

    p1 = Pupil(pupil1)
    print p1.name, p1.age

    p4 = Pupil(pupil4)
    print p4.name, p4.age, p4.children, p4.wife

    p5 = StrictPupil(pupil4)
    # should fail with attempt to access field 'wife'
    try:
        print p5.name, p5.age, p5.children, p5.wife
    except:
        print 'no wife'

    pup = JsonParser.from_json(pupil1, Pupil)
    print pup.name, pup.age

    pups = JsonParser.from_json(pupils, Pupil)
    print pups[0].name, pups[0].age
