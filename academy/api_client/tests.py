from django.test import TestCase
from json_object import JsonParser as JP, JsonObject, MissingRequiredFieldError

import collections

class JsonObjectTestClass(JsonObject):
    required_fields = ['name', 'age']

# Create your tests here.
class JsonObjectTest(TestCase):
    def setUp(self):
        '''
        Setup json strings for objects and arrays
        '''

        self.json_string = '{"name":"Martyn", "age":21}'
        self.json_array = '[{"name":"Martyn", "age":21},{"name":"Matt", "age":19}]'

    def test_parsed_object_from_json_string(self):
        output = JP.from_json(self.json_string)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertEqual(output.name, "Martyn")
        self.assertEqual(output.age, 21)

    def test_parsed_array_from_json(self):
        output = JP.from_json(self.json_array)

        self.assertTrue(isinstance(output, collections.Iterable))
        for json_object in output:
            self.assertTrue(isinstance(json_object, JsonObject))

        self.assertEqual(output[0].name, "Martyn")
        self.assertEqual(output[0].age, 21)
        self.assertEqual(output[1].name, "Matt")
        self.assertEqual(output[1].age, 19)

    def test_parsed_object_class(self):
        output = JP.from_json(self.json_string, JsonObjectTestClass)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertTrue(isinstance(output, JsonObjectTestClass))

    def test_parsed_array_object_class(self):
        output = JP.from_json(self.json_array, JsonObjectTestClass)

        self.assertTrue(isinstance(output, collections.Iterable))
        for json_object in output:
            self.assertTrue(isinstance(json_object, JsonObject))
            self.assertTrue(isinstance(json_object, JsonObjectTestClass))

        self.assertEqual(output[0].name, "Martyn")
        self.assertEqual(output[0].age, 21)
        self.assertEqual(output[1].name, "Matt")
        self.assertEqual(output[1].age, 19)

    def test_missing_required_field(self):
        light_json = '{"name":"Martyn"}'
        output = JP.from_json(light_json)

        self.assertTrue(isinstance(output, JsonObject))
        self.assertEqual(output.name, "Martyn")

        with self.assertRaises(MissingRequiredFieldError):
            JP.from_json(light_json, JsonObjectTestClass)
