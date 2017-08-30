"""
Generic CSV related methods
"""

import csv

from django.http import HttpResponse


class CSVWriter(object):
    """
    Generic CSV writer; can write to any writable objects
    """

    def __init__(self, csv_file, fields, data, header=True):
        """
        Args:
            csv_file: any writable object, (files or http responses etc)
            fields: ordered dict of the form {field_title: (field_key, default_value)}
            data: the data to write; list of dicts
            header (boolean): write header row or not; default true
        """
        self.csv_file = csv_file
        self.fields = fields
        self.data = data
        self.header = header

    def write_csv(self):
        """
        Writes rows and returns the written file
        """
        writer = csv.writer(self.csv_file, quoting=csv.QUOTE_ALL)

        # write the header row
        if self.header:
            writer.writerow(self.fields.keys())

        for record in self.data:
            row = [
                record.get(field, default_value)
                for field, default_value in self.fields.values()
            ]

            writer.writerow(row)

        return self.csv_file


def csv_file_response(file_name, fields={}, data=[], header=True):
    """
    Returns a HttpResponse with CSV file
    uses CSVWriter to write csv data

    Args:
        file_name: file name of csv attachment
        fields: fields of csv file
        data: data to write in csv cells
        header: include header row or not
    """
    if '.csv' not in file_name:
        file_name = '{}.csv'.format(file_name)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename={}".format(file_name)

    csv_writer = CSVWriter(response, fields, data, header)
    response = csv_writer.write_csv()

    return response
