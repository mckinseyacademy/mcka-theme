# -*- coding: utf-8 -*-

""" Tests for utility methods in data_sanitizing.py """
from collections import OrderedDict
import unittest
import csv

from django.core.files.uploadedfile import SimpleUploadedFile

from util.csv_helpers import CSVWriter


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
        reader = csv.DictReader(csv_file)

        # test header row written correctly
        self.assertListEqual(reader.fieldnames, fields.keys())

        # test rows values are written
        data_values = [t.values() for t in test_data]
        for row in reader:
            self.assertTrue(row.values() in data_values)
