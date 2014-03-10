from django.test import TestCase
from json_object import JsonParser as JP, JsonObject, MissingRequiredFieldError

import collections

class JsonObjectTestRequiredFieldsClass(JsonObject):
    required_fields = ['name', 'age']

class JsonObjectTestValidFieldsClass(JsonObject):
    valid_fields = ['name', 'age']

class JsonObjectTestRequiredAndValidFieldsClass(JsonObject):
    required_fields = ['name', 'age']
    valid_fields = ['name', 'age', 'gender']


# Create your tests here.
class JsonObjectTest(TestCase):
    def setUp(self):
        '''
        Setup json strings for objects and arrays
        '''
        self.json_string = '{"name":"Martyn", "age":21}'
        self.json_array = '[{"name":"Martyn", "age":21},{"name":"Matt", "age":19}]'

    def test_parsed_object_from_json_string(self):
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
        output = JP.from_json(self.json_string, JsonObjectTestRequiredFieldsClass)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertTrue(isinstance(output, JsonObjectTestRequiredFieldsClass))

    def test_parsed_array_object_class(self):
        '''
        Corresponding array of requested specific class
        '''
        output = JP.from_json(self.json_array, JsonObjectTestRequiredFieldsClass)

        self.assertTrue(isinstance(output, collections.Iterable))
        for json_object in output:
            self.assertTrue(isinstance(json_object, JsonObject))
            self.assertTrue(isinstance(json_object, JsonObjectTestRequiredFieldsClass))

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
            undefined_value = output.gender

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
            self.assertTrue(isinstance(json_object, JsonObjectTestValidFieldsClass))

        self.assertEqual(output[0].name, "Martyn")
        self.assertEqual(output[0].age, 21)
        with self.assertRaises(AttributeError):
            undefined_value = output[0].gender
        with self.assertRaises(AttributeError):
            undefined_value = output[0].sport

        self.assertEqual(output[1].name, "Matt")
        self.assertEqual(output[1].age, 19)
        with self.assertRaises(AttributeError):
            undefined_value = output[1].gender
        with self.assertRaises(AttributeError):
            undefined_value = output[1].sport

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

        output = JP.from_json(json_string, JsonObjectTestRequiredAndValidFieldsClass)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertTrue(isinstance(output, JsonObjectTestRequiredAndValidFieldsClass))
        self.assertEqual(output.name, "Martyn")
        self.assertEqual(output.age, 21)
        self.assertEqual(output.gender, "male")
