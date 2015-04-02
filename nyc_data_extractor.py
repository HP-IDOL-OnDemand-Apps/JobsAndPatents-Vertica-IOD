#!/usr/bin/env python

'''
    Script Explaining usages of HP IDOL OnDemand apis.
        In this example we would use query index api to get the patents
        of the companies from our NY database
        And we will also use entity extraction api to get the email
        address of the company from its homepage
'''
import sys
import os
import json
import optparse
'''
   Additioal packages required:
       1) If pip is not installed
           $ sudo apt-get install pip
       2) pyodbc
           $ sudo pip install --allow-external pyodbc --allow-unverified \
           > pyodbc pyodbc
       3) Install Vertica drivers.
           http://my.vertica.com/docs/6.1.x/HTML/index.htm#11699.htm
       4) configure odbc
       Add driver info do /etc/odbcinst.ini

           [HPVertica]
           Description = HP Vertica ODBC Driver
           Driver = /opt/vertica/lib64/libverticaodbc.so
'''
import requests
import pyodbc
from csv_parser import CsvParser


class NYDatasetAnalyser:
    def __init__(self, options):
        self.options = options
        # json config file will contain all the api urls, auth tokens
        # and the db connection details
        config_file = open(self.options.config_file)
        self.config = json.load(config_file)
        config_file.close()
        # Initialize the csv parser which will help us in reading the
        # csv data source
        self.csv_parser = CsvParser()
        # setup the database connection
        self.setup_db()

    def setup_db(self):
        db_info = self.config["db-info"]
        conn = pyodbc.connect(
            "DRIVER=%s;SERVER=%s;DATABASE=%s;PORT=%d;UID=%s;" % (
                db_info["vertica_driver"],
                db_info["server-ip"],
                db_info["db_name"],
                db_info["port"],
                db_info["username"]
            )
        )
        self.cursor = conn.cursor()

    def process_ny_data(self):
        # schema to read the csv file into the dict
        # Eg: for schema value "url": 5,
        #    we read the value at position 5 into the dict['url']
        schema = {
            "company_name": 0,
            "address": 1,
            "address2": 2,
            "city": 3,
            "category_name": 4,
            "url": 5,
            "hiring": 6,
            "jobs_url": 7,
            "why_nyc": 8
        }
        for data_dict in self.csv_parser.parse_file(
                self.options.input_file, schema
                ):
            # using try expect here , as the api calls few times(maybe
            # due to server issue or high load
            try:
                data_dict["email"] = self.extract_email(data_dict["url"])
            except:
                data_dict["email"] = ""
            # Insert the record into the company info table
            self.cursor.execute(
                "INSERT into company_info values(?, ?, ?, ?,?, ?, ?, ?,?, ?);",
                (data_dict["company_name"], data_dict["address"],
                 data_dict["address2"], data_dict["city"],
                 data_dict["category_name"], data_dict["url"],
                 data_dict["hiring"], data_dict["jobs_url"],
                 data_dict["why_nyc"], data_dict["email"]
                 )
            )

            self.cursor.execute("commit;")
            try:
                patent_info = self.get_patent(data_dict["company_name"])
                if patent_info.get("documents"):
                    for pattern in patent_info["documents"]:
                        title = pattern.get("title", "")
                        author = ",".join(pattern.get("patent_inventor", []))
                        company = data_dict["company_name"]
                        ref = pattern.get("reference", "")
                        company, title, author, ref = [
                            str(item)
                            for item
                            in [company, title, author, ref]
                        ]
                        self.cursor.execute(
                            "INSERT into patent_info values(?,?,?,?);",
                            (company, title, author, ref)
                        )
                        self.cursor.execute("commit;")
            except:
                print "error: during ", data_dict, " ", sys.exc_info()[0]

    def extract_email(self, url):
        ''' Extracts email address in the given page.
            here we try to find the email address of the company using
            companys home page and the hp idol entity extraction api.
            Params: url
            return values: email address separated by url
        '''
        url_params = {
            "url": url,
            "apikey": self.config["apikey"],
            "entity_type": "internet_email"
        }
        response = requests.get(
            self.config["api-baseurls"]["entity-extraction"],
            params=url_params
        )
        response_dict = json.loads(response.text)
        email_address = set()
        if response_dict.get("entities", {}):
            for data in response_dict["entities"]:
                email_address.add(data["original_text"])
        return str("<>".join(email_address))

    def get_patent(self, company_name):
        '''
            get_patent: gets the list of patents filed by the company
            here we use hp query text index api, which has pre created
            patent index.
            here we do exact search against the patent_assigness i.e
            the company
        '''
        url_params = {
            "text": "*",
            "field_text": "MATCH{%s}:patent_assignee" % company_name,
            "absolute_max_results": "10000",
            "indexes": "patents",
            "apikey": self.config["apikey"]
        }
        r = requests.get(
            self.config["api-baseurls"]["query-text"],
            params=url_params
        )
        return json.loads(r.text)

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option(
        '-c', '--config-file', default='config.json',
        help='Config having the resourceurl and log file name'
    )
    parser.add_option(
        '-i', '--input-file', default='resource/nyc_company_data.csv',
        help='Input data file'
    )
    options, args = parser.parse_args()

    ny_analyser = NYDatasetAnalyser(options)
    ny_analyser.process_ny_data()
