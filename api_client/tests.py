''' Tests for api_client calls '''
from django.test import TestCase
from .json_object import JsonParser as JP, JsonObject, MissingRequiredFieldError
from .user_models import UserResponse, AuthenticationResponse

import collections

# disable no-member 'cos the members are getting created from the json
# and some others that we don't care about for tests
# pylint: disable=no-member,line-too-long,too-few-public-methods,missing-docstring,too-many-public-methods,pointless-statement

class JsonObjectTestRequiredFieldsClass(JsonObject):
    required_fields = ['name', 'age']


class JsonObjectTestValidFieldsClass(JsonObject):
    valid_fields = ['name', 'age']


class JsonObjectTestRequiredAndValidFieldsClass(JsonObject):
    required_fields = ['name', 'age']
    valid_fields = ['name', 'age', 'gender']


class JsonObjectTestNestedClass(JsonObject):
    required_fields = ['one', 'two', 'three']


class JsonObjectTestNestingClass(JsonObject):
    required_fields = ['id', 'info']
    object_map = {
        'info': JsonObjectTestNestedClass
    }


class JsonObjectTestNestedNestingClass(JsonObject):
    required_fields = ['id', 'info']
    object_map = {
        'info': JsonObjectTestNestingClass
    }

# Create your tests here.


class JsonObjectTest(TestCase):

    def setUp(self):
        '''
        Setup json strings for objects and arrays
        '''
        self.json_string = '{"name":"Martyn", "age":21}'
        self.json_array = '[{"name":"Martyn", "age":21},{"name":"Matt", "age":19}]'

        self.nested_json = '{"id":22, "info":{"one":"a", "two":"b", "three":"c"}}'
        self.nested_array = '[{"id":22, "info":{"one":"a", "two":"b", "three":"c"}},{"id":23, "info":{"one":"x", "two":"y", "three":"z"}}]'

        self.nested_nest = '{"id":101, "info": [{"id":22, "info":{"one":"a", "two":"b", "three":"c"}},{"id":23, "info":{"one":"x", "two":"y", "three":"z"}}]}'

    def test_authentication_response(self):
        json_string = '{"token": "ceac67d033b98fbc5edd483a0e609193","expires": 1209600,"user": {"id": 4,"email": "staff@example.com","username": "staff"}}'
        output = JP.from_json(json_string, AuthenticationResponse)

        self.assertTrue(isinstance(output, AuthenticationResponse))
        self.assertTrue(isinstance(output.user, UserResponse))

    def test_parsed_object_from_json(self):
        '''
        Default behaviour yeilds base class JsonObject with appropriate fields
        '''
        output = JP.from_json(self.json_string)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertEqual(output.name, "Martyn")
        self.assertEqual(output.age, 21)

    def test_parsed_array_from_json(self):
        '''
        Corresponding array of JsonObject objects
        '''
        output = JP.from_json(self.json_array)

        self.assertTrue(isinstance(output, collections.Iterable))
        for json_object in output:
            self.assertTrue(isinstance(json_object, JsonObject))

        self.assertEqual(output[0].name, "Martyn")
        self.assertEqual(output[0].age, 21)
        self.assertEqual(output[1].name, "Matt")
        self.assertEqual(output[1].age, 19)

    def test_parsed_object_class(self):
        '''
        When requesting specific class, result yeilds specific class
        '''
        output = JP.from_json(
            self.json_string, JsonObjectTestRequiredFieldsClass)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertTrue(isinstance(output, JsonObjectTestRequiredFieldsClass))

    def test_parsed_array_object_class(self):
        '''
        Corresponding array of requested specific class
        '''
        output = JP.from_json(
            self.json_array, JsonObjectTestRequiredFieldsClass)

        self.assertTrue(isinstance(output, collections.Iterable))
        for json_object in output:
            self.assertTrue(isinstance(json_object, JsonObject))
            self.assertTrue(
                isinstance(json_object, JsonObjectTestRequiredFieldsClass))

        self.assertEqual(output[0].name, "Martyn")
        self.assertEqual(output[0].age, 21)
        self.assertEqual(output[1].name, "Matt")
        self.assertEqual(output[1].age, 19)

    def test_missing_required_field(self):
        '''
        If required field is missing, should have an exception
        '''
        light_json = '{"name":"Martyn"}'
        output = JP.from_json(light_json)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertEqual(output.name, "Martyn")

        with self.assertRaises(MissingRequiredFieldError):
            JP.from_json(light_json, JsonObjectTestRequiredFieldsClass)

    def test_valid_fields(self):
        '''
        If valid fields are provided, only required and valid fields should be accessible
        No exception if json contains additional fields, but these are dropped from results
        '''
        json_string = '{"name":"Martyn", "age":21, "gender":"male"}'

        output = JP.from_json(json_string, JsonObjectTestValidFieldsClass)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertTrue(isinstance(output, JsonObjectTestValidFieldsClass))

        self.assertEqual(output.name, "Martyn")
        self.assertEqual(output.age, 21)
        with self.assertRaises(AttributeError):
            output.gender

    def test_array_valid_fields(self):
        '''
        If valid fields are provided, only required and valid fields should be accessible
        No exception if json contains additional fields, but these are dropped from results
        '''
        json_string = '[{"name":"Martyn", "age":21, "gender":"male"}, {"name":"Matt", "age":19, "sport":"mountaineering"}]'

        output = JP.from_json(json_string, JsonObjectTestValidFieldsClass)

        self.assertTrue(isinstance(output, collections.Iterable))
        for json_object in output:
            self.assertTrue(isinstance(json_object, JsonObject))
            self.assertTrue(
                isinstance(json_object, JsonObjectTestValidFieldsClass))

        self.assertEqual(output[0].name, "Martyn")
        self.assertEqual(output[0].age, 21)
        with self.assertRaises(AttributeError):
            output[0].gender
        with self.assertRaises(AttributeError):
            output[0].sport

        self.assertEqual(output[1].name, "Matt")
        self.assertEqual(output[1].age, 19)
        with self.assertRaises(AttributeError):
            output[1].gender
        with self.assertRaises(AttributeError):
            output[1].sport

    def test_valid_not_required_fields(self):
        json_string = '{"name":"Martyn"}'

        output = JP.from_json(json_string, JsonObjectTestValidFieldsClass)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertTrue(isinstance(output, JsonObjectTestValidFieldsClass))

        self.assertEqual(output.name, "Martyn")
        # unspecified but valid value raises error - are we okay with this?
        with self.assertRaises(AttributeError):
            self.assertEqual(output.age, 21)

        json_string = '{"name":"Martyn", "age":21, "additional":"extra"}'

        output = JP.from_json(json_string, JsonObjectTestValidFieldsClass)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertTrue(isinstance(output, JsonObjectTestValidFieldsClass))

        self.assertEqual(output.name, "Martyn")
        self.assertEqual(output.age, 21)
        # specified field, but invalid raises error
        with self.assertRaises(AttributeError):
            self.assertEqual(output.additional, "extra")

    def test_valid_and_required(self):
        json_string = '{"name":"Martyn", "age":21, "gender":"male"}'

        output = JP.from_json(
            json_string, JsonObjectTestRequiredAndValidFieldsClass)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertTrue(
            isinstance(output, JsonObjectTestRequiredAndValidFieldsClass))
        self.assertEqual(output.name, "Martyn")
        self.assertEqual(output.age, 21)
        self.assertEqual(output.gender, "male")

    def test_nested_type(self):
        '''
        Consider when object type is nested within another
        '''
        output = JP.from_json(self.nested_json, JsonObjectTestNestingClass)

        self.assertTrue(isinstance(output, JsonObjectTestNestingClass))
        self.assertTrue(isinstance(output.info, JsonObjectTestNestedClass))

    def test_nested_array(self):
        '''
        Consider when object type is nested within another
        '''
        output = JP.from_json(self.nested_array, JsonObjectTestNestingClass)

        self.assertTrue(isinstance(output[0], JsonObjectTestNestingClass))
        self.assertTrue(isinstance(output[0].info, JsonObjectTestNestedClass))
        self.assertTrue(isinstance(output[1], JsonObjectTestNestingClass))
        self.assertTrue(isinstance(output[1].info, JsonObjectTestNestedClass))

    def test_nested_nest(self):
        output = JP.from_json(
            self.nested_nest, JsonObjectTestNestedNestingClass)

        self.assertTrue(isinstance(output, JsonObjectTestNestedNestingClass))
        self.assertTrue(isinstance(output.info[0], JsonObjectTestNestingClass))
        self.assertTrue(
            isinstance(output.info[0].info, JsonObjectTestNestedClass))

    def test_groups(self):
        output = JP.from_json('[{"name": "super_admin","id":1234,"uri": "/api/users/14/groups/1234"},{"name": "sub_admin","id":1357,"uri": "/api/users/14/groups/1357"},{"name": "company_admin","id":5678,"uri": "/api/users/14/groups/5678"},{"name": "arbitrary_group","id":2468,"uri": "/api/users/14/groups/2468"}]')

        self.assertTrue(len(output)==4)
        self.assertTrue(output[0].name == "super_admin")
