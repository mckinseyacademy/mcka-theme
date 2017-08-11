"""
Generic CSV related methods
"""

import csv


class CSVWriter(object):
    """
    Generic CSV writer; can write to any writable objects
    """

    def __init__(self, csv_file, fields, data):
        """
        Args:
            csv_file: any writable object, (files or http responses etc)
            fields: ordered dict of the form {field_title: (field_key, default_value)}
            data: the data to write; list of dicts
        """
        self.csv_file = csv_file
        self.fields = fields
        self.data = data

    def write_csv(self):
        """
        Writes rows and returns the written file
        """
        writer = csv.writer(self.csv_file, quoting=csv.QUOTE_ALL)

        # write the header row
        writer.writerow(self.fields.keys())

        for record in self.data:
            row = [
                record.get(field, default_value)
                for field, default_value in self.fields.values()
            ]

            writer.writerow(row)

        return self.csv_file
