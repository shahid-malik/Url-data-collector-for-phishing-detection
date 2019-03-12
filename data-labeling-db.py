from datetime import datetime
import os
import sys
import socket
import time

import mysql.connector
from app import get_current_time
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
import config

reload(sys)
sys.setdefaultencoding('utf8')


def get_current_time():
    """
    Get current time in the (year-month-date Hour-minute-Second) format
    :return:
    """
    ts = time.time()
    timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


class Connection:
    """
    Data Base connection class
    """

    def __init__(self):
        """ constructor for connection class """
        if socket.gethostbyname(socket.gethostname()) == '127.0.1.1':
            self.DATABASE_CONFIG = config.LOCAL_DATABASE_CONFIG
        else:
            self.DATABASE_CONFIG = config.PROD_DATABASE_CONFIG

        self.table = self.DATABASE_CONFIG['db_table']
        self.host = self.DATABASE_CONFIG['host']
        self.user = self.DATABASE_CONFIG['user']
        self.password = self.DATABASE_CONFIG['password']
        self.db = self.DATABASE_CONFIG['dbname']

    def connect(self):
        """ Create a mysql database connection        """
        con = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db,
            charset='utf8',
            use_unicode=True
        )
        return con

    def update_db_url_data(self, url_data):
        """ Update URL in the in the table (Package_features) for verdict and verdict timestamp        """
        con = self.connect()
        update_query = "update %s set verdict='%s', verdict_update_timestamp='%s' where url_md5 like '%s';" % (
            self.table, url_data['verdict'], url_data['verdict_timestamp'], url_data['url_md5'])

        query_status = self.execute_query(con, update_query)
        if query_status:
            print("  -----  Data Updated Successfully  ...... ")

    @staticmethod
    def execute_query(con, query):
        """ Given any query and database connection, this function will execute the query and return the status True
        if successful
        """
        cursor = con.cursor()
        try:
            cursor.execute("set names utf8;")
            cursor.execute('SET CHARACTER SET utf8;')
            cursor.execute('SET character_set_connection=utf8;')
            cursor.execute(query)
            con.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)


class URL:
    """
    Main URL class, It contains all the url processing logic
    """

    def __init__(self):
        """
        Constructor
        """
        self.verdict = 'Benign'
        self.verdict_timestamp = get_current_time()
        self.con = Connection()

    @staticmethod
    def get_url_verdict(url):
        """
        Get the verdict from csv file. This csv file is been generated from outer system,
        got a csv file from the external file and place it in the lib folder with the name
        urls_verdict_result_v1.csv
        :param url:
        :return:
        """
        if 'Malicious' in url:
            verdict = "Malicious"
        else:
            verdict = "Benign"
        return verdict

    def read_url_file(self, in_file):
        """
        Function to read the csv file of urls with verdict to insert into the database
        :param in_file:
        :return:
        """
        url_dict = {}
        mal_counter = 0
        try:
            with open(in_file) as f:
                input_urls = f.readlines()
                for url in input_urls:
                    verdict = self.get_url_verdict(url)
                    if verdict == "Malicious":
                        mal_counter += 1

                    url_dict.update({
                        'url_md5': url.split(',')[0],
                        'verdict': verdict,
                        'verdict_timestamp': get_current_time()
                    })

                    self.con.update_db_url_data(url_dict)
            print("Total Malicious", mal_counter)
        except Exception as e:
            print("Exception Occurs: %s" % e)
            return False


def main():
    """
    Main execution to start the processing for a url
    :return:
    """
    args = sys.argv
    if len(args) > 2 or len(args) < 2:
        print("Please provide the arguments in order as shown in example command")
        print("\npython data-labeling-db.py file path \nor\npython data-labeling-db.py /home/shahid/v2\n")
        sys.exit(1)
    else:
        file_path = args[1]
        urls = URL()
        urls.read_url_file(file_path)


if __name__ == "__main__":
    main()
