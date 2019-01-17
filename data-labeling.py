import os
import sys
import socket
import mysql.connector
from app import get_current_time
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
import config
reload(sys)
sys.setdefaultencoding('utf8')


def execute_query(con, query):
    """
    Given any query and database connection, this function will execute the query and return the status True
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


class Connection:

    def __init__(self):
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
        """
        Create a mysql database connection
        :return:
        :return:
        """
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
        """
        Update URL in the in the table (Package_features) for verdict and verdict timestamp
        :return:
        """
        con = self.connect()
        update_query = "update %s set verdict='%s', verdict_update_timestamp='%s' where url_md5 like '%s';" % (
            self.table, url_data['verdict'], url_data['verdict_timestamp'], url_data['url_md5'])

        query_status = execute_query(con, update_query)
        if query_status:
            print("  -----  Data Updated Successfully  ...... ")


def get_url_verdict(url):
    if 'Malicious' in url:
        verdict = "Malicious"
    else:
        verdict = "Benign"
    return verdict


class URL:

    def __init__(self):
        self.verdict = 'Benign'
        self.verdict_timestamp = get_current_time()
        self.con = Connection()

    def read_url_file(self, in_file):
        """
        Function to read the csv file of urls with verdict to insert into the database
        :param in_file:
        :return:
        """
        url_dict = {}
        try:
            with open(in_file) as f:
                input_urls = f.readlines()
                for url in input_urls:
                    verdict = get_url_verdict(url)
                    url_dict.update({
                        'url_md5': url.split(',')[0],
                        'verdict': verdict,
                        'verdict_timestamp': get_current_time()
                    })

                    self.con.update_db_url_data(url_dict)
        except:
            return False


if __name__ == "__main__":
    cur_dir = os.path.dirname(__file__)
    file_name = "urls_verdict_result"
    file_version = "v1"
    file_path = cur_dir+'/lib/'+file_name+'_'+file_version+'.csv'

    urls = URL()
    urls.read_url_file(file_path)
