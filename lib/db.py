import mysql.connector
from mysql.connector import MySQLConnection, Error
# import pymysql
import sys
import os
import socket
import hashlib

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
import config


def connect_db():
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
        db=DATABASE_CONFIG['dbname']
    )
    return con


def execute_query(con, query):
    cursor = con.cursor()
    try:
        cursor.execute(query)
        con.commit()
        cursor.close()
        return True
    except Exception as e:
        print(e)
        pass


def add_column(con, table, col_name):
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

#
if __name__ == "__main__":
    DATA_TABLE = "package_features"
    main()
#     COLUMN_NAME = "test"
#     data_dict = {'url_length': 21, 'domain': 'http://solitinera.com/',
#                  'url_favicons': '3f8c936116dbf3b30b875e12ab2268e2,3f8c936116dbf3b30b875e12ab2268e2',
#                  'url_file_type': 'text/html', 'domain_total_og_links': 22, 'url_total_favicon': 2,
#                  'timestamp': '2019-01-08 16:00:02', 'domain_total_favicon': 2,
#                  'domain_base64': 'aHR0cDovL3NvbGl0aW5lcmEuY29t', 'url_total_og_domains': 8,
#                  'domain_entropy': 3.880179922675737, 'domain_isHtml': True,
#                  'landing_url_base64': 'aHR0cHM6Ly93d3cuc29saXRpbmVyYS5jb20v', 'title_match': True,
#                  'domain_page_title': 'Sol\'itinera l Reportage l France', 'url_base64': 'aHR0cDovL3NvbGl0aW5lcmEuY29t',
#                  'domain_file_type': 'text/html', 'url': 'http://solitinera.com',
#                  'domain_content_type': 'text/html;charset=utf-8', 'url_isHtml': True,
#                  'url_og_domains': 'bcbafb69b52516b1733a52b737d2d4b7,e203e98e4c606735cf56db84a002fd22,5f395d3a47e44537ade5365501edc4d1,f3781a2a0339b51700002c01f505c91c,8f5d4f2405f1acd49e7eb3bd0212ccc4,e9efa78d624d92773b6cd944a094f8c6,dba51bcc527ba93f7fe03868747280d5,d41d8cd98f00b204e9800998ecf8427e',
#                  'domain_total_og_domains': 8, 'uri_length': 0, 'url_md5': 'cc44418a1a39ed7a29e75836b7b56f4a',
#                  'url_entropy': 3.880179922675737, 'url_content_type': 'text/html;charset=utf-8',
#                  'landing_url_hash': '8f5d4f2405f1acd49e7eb3bd0212ccc4',
#                  'domain_md5': 'cc44418a1a39ed7a29e75836b7b56f4a', 'url_total_og_links': 22,
#                  'url_page_title': 'Sol\'\itinera l Reportage l France',
#                  'domain_og_domains': 'bcbafb69b52516b1733a52b737d2d4b7,e203e98e4c606735cf56db84a002fd22,5f395d3a47e44537ade5365501edc4d1,f3781a2a0339b51700002c01f505c91c,8f5d4f2405f1acd49e7eb3bd0212ccc4,e9efa78d624d92773b6cd944a094f8c6,dba51bcc527ba93f7fe03868747280d5,d41d8cd98f00b204e9800998ecf8427e',
#                  'domain_favicons': '3f8c936116dbf3b30b875e12ab2268e2,3f8c936116dbf3b30b875e12ab2268e2'}
#     insert_data("package_features", data_dict)

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
