# -*- coding: utf-8 -*-

""" Tests for utility methods in data_sanitizing.py """
from collections import OrderedDict
import unittest
import unicodecsv

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse

from util.csv_helpers import CSVWriter, csv_file_response


class TestCSVWriter(unittest.TestCase):
    """
    Test cases for CSV writer class
    """
    def setUp(self):
        """
        sets things up
        """
        self.csv_file = SimpleUploadedFile(
            'abc.csv',
            '',
            content_type='text/csv'
        )

    def test_initialization(self):
        csv_writer = CSVWriter(self.csv_file, dict(), [])

        self.assertIsInstance(csv_writer, CSVWriter)

    def test_write_csv(self):
        """
        Tests writing headers and rows to file
        """
        test_data = [
            {'name': 'test1', 'tech': 'Django'},
            {'name': 'test2', 'tech': 'Python'}
        ]

        fields = OrderedDict([('Name', ('name', '')), ('Technology', ('tech', ''))])

        csv_writer = CSVWriter(self.csv_file, fields, test_data)
        csv_file = csv_writer.write_csv()

        csv_file.open()
        reader = unicodecsv.DictReader(csv_file)

        # test header row written correctly
        self.assertCountEqual(list([d for d in reader][0].keys()), list(fields.keys()))

        # test rows values are written
        data_values = [list(t.values()) for t in test_data]
        for row in reader:
            self.assertTrue(list(row.values()) in data_values)


class TestCSVHttpResponse(unittest.TestCase):
    def test_csv_file_response(self):
        """
        Tests csv file response
        """
        test_data = [
            {'name': 'test1', 'tech': 'Django'},
            {'name': 'test2', 'tech': 'Python'}
        ]

        fields = OrderedDict([('Name', ('name', '')), ('Technology', ('tech', ''))])

        response = csv_file_response(
            file_name='test_file', fields=fields,
            data=test_data, header=False
        )

        reader = unicodecsv.DictReader(response)

        # test it's an Http response
        self.assertIsInstance(response, HttpResponse)

        # test rows values are written and identical
        test_values = [d for t in test_data for d in list(t.values())]
        response_values = [d for row in reader for v in list(row.values()) for d in v]
        self.assertCountEqual(response_values, test_values)
