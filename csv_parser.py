import csv
import re


class CsvParser:
    def __init__(self, delimiter=',', quotechar='"'):
        self.delimiter = delimiter
        self.quotechar = quotechar

    def parse_file(self, fileloc, schema):
        ''' Parse the given csv file with schema
            Params: fileloc -> file location
                    schema -> schema with which we need to parse
            Return: Generator that yields the data corresponding to
                    the given schema
        '''
        with open(fileloc, 'rb') as csvfile:
            for line in csv.reader(
                    csvfile,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar
                    ):
                data = {}
                for key, index in schema.items():
                    data[key] = line[index]
                yield data
