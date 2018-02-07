"""
Generic CSV related methods
"""

import unicodecsv
import csv, codecs, cStringIO
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
        writer = unicodecsv.writer(self.csv_file)

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


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") if isinstance(s, basestring) else str(s) for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
