import mysql.connector
# import pymysql
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
import config


def connect_db(db_name):
    if db_name != config.LOCAL_DATABASE_CONFIG['dbname']:
        raise ValueError("Could not find DB with given name")

    con = mysql.connector.connect(
        host=config.LOCAL_DATABASE_CONFIG['host'],
        user=config.LOCAL_DATABASE_CONFIG['user'],
        password=config.LOCAL_DATABASE_CONFIG['password'],
        db=config.LOCAL_DATABASE_CONFIG['dbname']
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
    ADD_DATA_TABLE_QUERY = "ALTER TABLE %s ADD %s varchar(255)" % (table, col_name)
    try:
        query_status = execute_query(con, ADD_DATA_TABLE_QUERY)
        if query_status:
            print("Column added successfully")
    except Exception as e:
        print("Issue adding new column to the table with exception", e)
        pass


def insert_data(table, data_dict):
    con = connect_db("headless")
    data_insertion_query = "insert into %s (url_md5, url_base64, url_title, url_favicons, url_is_html, " \
                           "url_content_type, url_total_favicon, url_og_domains, url_total_og_domains, " \
                           "url_total_og_links, url_file_type, domain_md5, domain_base64, domain_title, " \
                           "domain_favicons, domain_is_html, domain_content_type, domain_total_favicon, " \
                           "domain_og_domains, domain_total_og_domains, domain_total_og_links, domain_file_type, " \
                           "landing_url_hash, landing_url_base64, title_match, uri_length, url_length) VALUES ('%s', " \
                           "'%s', '%s', '%s', " \
                           "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', " \
                           "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" \
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
                              data_dict['url_length']
                              )
    query_status = execute_query(con, data_insertion_query)
    if query_status:
        print("Data Inserted Successfully")

def main():
    conn = connect_db("headless")
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
    # add_column(conn, DATA_TABLE, 'domain_entropy')
    # conn.close()
    (insert_data(DATA_TABLE, data))


if __name__ == "__main__":
    DATA_TABLE = "package_features"
    COLUMN_NAME = "test"
    DATA_TABLE_QUERY = "create table %s ( url_md5 varchar(255), url_base64 varchar(255), url_title varchar(255), " \
                       "url_favicons varchar(255), url_is_html varchar(255), 	url_content_type varchar(255), 	" \
                       "url_total_favicon varchar(255), url_og_domains varchar(35000), 	url_total_og_domains varchar(" \
                       "255), url_total_og_links varchar(255), 	url_file_type varchar(255), domain_md5 varchar(255)," \
                       "domain_base64 varchar(255),domain_title varchar(255), domain_favicons varchar(255),	" \
                       "domain_is_html varchar(255),domain_content_type varchar(255),	domain_total_favicon varchar(" \
                       "255), domain_og_domains varchar(35000), domain_total_og_domains varchar(255)," \
                       "domain_total_og_links varchar(255), domain_file_type varchar(255),landing_url_hash " \
                       "varchar(255), landing_url_base64 varchar(255), title_match varchar(255)) " % DATA_TABLE

    main()
