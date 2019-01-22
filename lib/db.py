import mysql.connector
from mysql.connector import MySQLConnection, Error
# import pymysql
import os
import socket
import hashlib
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
import config
reload(sys)
sys.setdefaultencoding('utf8')


def connect_db():
    """
    Create a mysql database connection
    :return:
    """
    if socket.gethostbyname(socket.gethostname()) == '127.0.1.1':
        DATABASE_CONFIG = config.LOCAL_DATABASE_CONFIG
    else:
        DATABASE_CONFIG = config.PROD_DATABASE_CONFIG
    #
    # if db_name != DATABASE_CONFIG['dbname']:
    #     raise ValueError("Could not find DB with given name")

    con = mysql.connector.connect(
        host=DATABASE_CONFIG['host'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        db=DATABASE_CONFIG['dbname'],
        charset='utf8',
        use_unicode=True
    )
    return con


def execute_query(con, query):
    """Given any query and database connection, this function will execute the query and return the status True
    if successful
    """
    # con.set_character_set('utf8')
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


def add_column(con, table, col_name):
    """
    Add a column to the table using alter table standard query
    :param con:
    :param table:
    :param col_name:
    :return:
    """
    ADD_DATA_TABLE_QUERY = "ALTER TABLE %s ADD %s varchar(50)" % (table, col_name)
    try:
        query_status = execute_query(con, ADD_DATA_TABLE_QUERY)
        if query_status:
            print("Column added successfully")
    except Exception as e:
        print("Issue adding new column to the table with exception", e)
        pass


def get_md5_hash(url):
    """
    generate md5 hash of the string, In this case, a url with http or https is provided for the synchronization
    throughout the code
    :param url:
    :return: md5 hash
    """
    try:
        m = hashlib.md5()
        m.update(url)
        md5_hash = m.hexdigest()
    except:
        md5_hash = ''
    return md5_hash


def insert_data(data_dict):
    """
    Insert data to the table (Package_features) using the query
    :param data_dict:
    :return:
    """
    table = 'package_features'
    con = connect_db()

    data_insertion_query = "insert into %s (url_md5, url_base64, url_title, url_favicons, url_is_html, " \
                           "url_content_type, url_total_favicon, url_og_domains, url_total_og_domains, " \
                           "url_total_og_links, url_file_type, domain_md5, domain_base64, domain_title, " \
                           "domain_favicons, domain_is_html, domain_content_type, domain_total_favicon, " \
                           "domain_og_domains, domain_total_og_domains, domain_total_og_links, domain_file_type, " \
                           "landing_url_hash, landing_url_base64, title_match, uri_length, url_length, " \
                           "is_favicon_match," \
                           "domain_entropy, url_entropy, timestamp, total_at_the_rate) VALUES ('%s', " \
                           "'%s', '%s', '%s', " \
                           "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', " \
                           "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" \
                           % (table,
                              data_dict['url_md5'],
                              data_dict['url_base64'],
                              data_dict['url_page_title'],
                              data_dict['url_favicons'],
                              data_dict['url_isHtml'],
                              data_dict['url_content_type'],
                              data_dict['url_total_favicon'],
                              data_dict['url_og_domains'],
                              data_dict['url_total_og_domains'],
                              data_dict['url_total_og_links'],
                              data_dict['url_file_type'],
                              data_dict['domain_md5'],
                              data_dict['domain_base64'],
                              data_dict['domain_page_title'],
                              data_dict['domain_favicons'],
                              data_dict['domain_isHtml'],
                              data_dict['domain_content_type'],
                              data_dict['domain_total_favicon'],
                              data_dict['domain_og_domains'],
                              data_dict['domain_total_og_domains'],
                              data_dict['domain_total_og_links'],
                              data_dict['domain_file_type'],
                              data_dict['landing_url_hash'],
                              data_dict['landing_url_base64'],
                              data_dict['title_match'],
                              data_dict['uri_length'],
                              data_dict['url_length'],

                              data_dict['is_favicon_match'],
                              data_dict['domain_entropy'],
                              data_dict['url_entropy'],
                              data_dict['timestamp'],
                              data_dict['total_at_the_rate'],

                              )
    query_status = execute_query(con, data_insertion_query)
    if query_status:
        print("  -----  Data Inserted Successfully  ...... ")


def check_if_url_processed(url):
    """
    Check if the url get from api is processed already based on url md5 hash which is also primary key
    if url is processed then get another url from api. url is processed only once
    :param url:
    :return:
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        url_hash = get_md5_hash(url)
        query = "select * from package_features where url_md5='%s';" % url_hash
        cursor.execute(query)
        total_rows = cursor.rowcount
        if total_rows < 1:
            conn.close()
            return True
        else:
            conn.close()
            return False
    except Error as e:
        print("Exception %s in check if url processed method" % e)


def main():
    """
    main function to execute the functionality
    :return:
    """
    conn = connect_db()
    DATA_TABLE = "package_features"
    data = {'url_md5': 'test', 'url_base64': 'test', 'url_title': 'test', 'url_favicons': 'test',
            'url_is_html': 'test', 'url_content_type': 'test', 'url_total_favicon': 'test', 'url_og_domains': 'test',
            'url_total_og_domains': 'test', 'url_total_og_links': 'test', 'url_file_type': 'test',
            'domain_md5': 'test', 'domain_base64': 'test', 'domain_title': 'test', 'domain_favicons': 'test',
            'domain_is_html': 'test', 'domain_content_type': 'test', 'domain_total_favicon': 'test',
            'domain_og_domains': 'test', 'domain_total_og_domains': 'test', 'domain_total_og_links': 'test',
            'domain_file_type': 'test', 'landing_url_hash': 'test', 'landing_url_base64': 'test', 'title_match': 'test'
            }
    # execute_query(conn, DATA_TABLE_QUERY)
    add_column(conn, DATA_TABLE, 'total_at_the_rate')
    conn.close()
    # (insert_data(DATA_TABLE, data))


# if __name__ == "__main__":

# DATA_TABLE_QUERY = "create table %s ( url_md5 varchar(255), url_base64 varchar(1000), url_title varchar(255), " \
#                    "url_favicons varchar(5000), url_is_html varchar(255), 	url_content_type varchar(255), 	" \
#                    "url_total_favicon varchar(255), url_og_domains varchar(15000), 	url_total_og_domains varchar(" \
#                    "255), url_total_og_links varchar(255), 	url_file_type varchar(255), domain_md5 varchar(255)," \
#                    "domain_base64 varchar(1000),domain_title varchar(255), domain_favicons varchar(5000),	" \
#                    "domain_is_html varchar(255),domain_content_type varchar(255),	domain_total_favicon varchar(" \
#                    "255), domain_og_domains varchar(15000), domain_total_og_domains varchar(255)," \
#                    "domain_total_og_links varchar(255), domain_file_type varchar(255),landing_url_hash " \
#                    "varchar(255), landing_url_base64 varchar(1000), title_match varchar(255)) " % DATA_TABLE
#
# main()
