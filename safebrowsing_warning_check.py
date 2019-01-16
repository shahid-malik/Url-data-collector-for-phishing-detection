import json
import sys
import os
import urllib2
import requests
import hashlib
import magic
import urllib
from BeautifulSoup import BeautifulSoup
from selenium import webdriver
from lib import html2txt
from selenium.common.exceptions import TimeoutException
requests.packages.urllib3.disable_warnings()
reload(sys)
sys.setdefaultencoding('utf8')


def get_md5_hash(in_url):
    """
    generate md5 hash of the string, In this case, a url with http or https is provided for the synchronization
    throughout the code
    :param in_url:
    :return: md5 hash
    """
    try:
        m = hashlib.md5()
        m.update(in_url)
        md5_hash = m.hexdigest()
    except:
        md5_hash = ''
    return md5_hash


def get_page_title(chrome_driver):
    """
    Get the title of the page hit by  given url, provide processed urls with the http or https protocol
    :param chrome_driver:
    :return: title (string)
    """
    # soup = BeautifulSoup(urllib2.urlopen(url))
    try:
        # title = soup.title.string
        title = chrome_driver.title.encode('ascii', 'replace')
        title = title.replace("'", "''")
    except Exception as exp:
        print("Error while extracting title from landing page with Exception \n %s" % exp)

        title = ''

    return title


def get_favicon_selenium(chrome_driver, directory):
    """
    Get favicons of the url given,
    :param chrome_driver: selenium driver with the url
    :param directory: directory to store the favicon
    :return: total favicon and list of favicon
    """
    total_favicons = 0
    rel = ""
    try:
        links = chrome_driver.find_elements_by_tag_name('link')
    except Exception as exp:
        print("Error getting favicon from landing page with Exception \n %s" % exp)
        return total_favicons

    for link in links:
        try:
            rel = link.get_attribute('rel')
        except Exception as exp:
            print("Error getting favicon links from landing page with Exception \n %s" % exp)

        if 'icon' in rel:
            href = link.get_attribute('href')
            favicon_ext = href.split('.')[-1]
            if not favicon_ext == 'svg':
                name = 'favicon_{}.ico'.format(total_favicons)
            else:
                name = 'favicon_{}.{}'.format(total_favicons, favicon_ext)
            try:
                icon = urllib2.urlopen(str(href))
                save_favicon_to_directory(icon, name, path=directory)
                total_favicons += 1
            except:
                pass
    return total_favicons


def save_favicon_to_directory(icon, name, path):
    """
    Save the favicon to the given directory.
    :param icon:
    :param name:
    :param path:
    :return:
    """
    name = path + name
    try:
        with open(name, "wb") as f:
            f.write(icon.read())
            f.close()
    except Exception as exp:
        print("Error while saving favicon to the directory \n %s" % exp)


def create_directory(dir_name):
    """
    Create packages directory on the local machine
    :param dir_name: directory path
    :return:
    """
    try:
        if not os.path.exists(dir_name):
            return os.makedirs(dir_name)
    except Exception as exp:
        print("ERROR creating %s Directory, Exiting the code" % dir_name, " | with Exception %s" % exp)
        sys.exit(1)


def get_og_links(chrome_driver):
    """
    get outgoing links for landing page of the url
    :param chrome_driver: selenium url driver
    :return: total outgoing links and list of og links
    """
    og_links = []
    total_og_links = 0
    try:
        a_tags = chrome_driver.find_elements_by_tag_name('a')
        for a_tag in a_tags:
            href = a_tag.get_attribute('href')
            og_links.append(href)
            total_og_links += 1
    except Exception as exp:
        print("Exceptions in getting outgoing links from the page %s" % exp)
    return [total_og_links, og_links]


def get_file_type(in_url):
    """
    Get the file type of the landing page on url
    :param in_url:
    :return:
    """
    mime = magic.Magic(mime=True)
    create_directory("tmp")
    output = "tmp/output.txt"
    try:
        status = urllib2.urlopen(in_url).code
        if status:
            urllib.urlretrieve(in_url, output)
            mimes = mime.from_file(output)
            return mimes
    except:
        return -1


def save_html(url_directory, chrome_driver):
    """
    Save html page of the url in the given directory
    :param url_directory:
    :param chrome_driver:
    :return:
    """
    try:
        page = chrome_driver.page_source.encode('utf-8')
        file_path = url_directory + 'page.html'
        file_ = open(url_directory + '/' + 'page.html', 'w')
        file_.write(page)
        file_.close()
        return file_path
    except Exception as exp:
        print("Exception %s in saving html to package" % exp)


def create_screenshot(directory_path, chrome_driver):
    """
    Create a screen shot of the url provided
    :return:
    :param directory_path:
    :param chrome_driver:
    :return:
    """
    try:
        screenshot_dir = directory_path + "screenshot.png"
        chrome_driver.save_screenshot(screenshot_dir)
        return True
    except Exception as exp:
        print("Exception in getting screenshot %s" % exp)


def create_package(in_url):
    """
    Create a package with domain and url directories
    :param in_url:
    :return:
    """
    proj_dir = os.path.dirname(os.path.realpath(__file__))
    data_directory = str(proj_dir) + "/fishing_package_data/"
    url_hash = get_md5_hash(in_url)
    PACKAGE_DIRECTORY = data_directory + url_hash + '/'
    create_directory(PACKAGE_DIRECTORY)
    if not in_url.endswith('/'):
        in_url += '/'

    URL_ICONS_DIRECTORY = PACKAGE_DIRECTORY + 'icons/'
    create_directory(PACKAGE_DIRECTORY)
    create_directory(URL_ICONS_DIRECTORY)
    return PACKAGE_DIRECTORY, URL_ICONS_DIRECTORY


def get_head_body(html_page):
    file_path = "file://%s" % html_page
    page = urllib2.urlopen(file_path).read()

    soup = BeautifulSoup(page)
    head = soup.find('head')
    body = soup.find('body')
    return len(head), len(body)


def get_url_attributes(url_directory, in_url, chrome_driver):
    """
    Get attributes from url
    :type in_url: object
    :param url_directory:
    :param in_url:
    :param chrome_driver:
    :return:
    """
    retry = 0
    data_obj = {}
    url_hash = get_md5_hash(in_url)
    while True:
        try:
            chrome_driver.get(in_url)

            create_screenshot(url_directory, chrome_driver)
            file_path = save_html(url_directory, chrome_driver)
            html2txt.text_from_html(url_directory, file_path)

            head, body = get_head_body(file_path)
            url_total_og_urls, url_og_urls_list = get_og_links(chrome_driver)
            url_total_favicons = get_favicon_selenium(chrome_driver, url_directory+'icons')
            page_title = get_page_title(chrome_driver)
            file_type = get_file_type(in_url)

            data_obj.update({
                    'url_md5': url_hash,
                    'url_page_title': page_title,
                    'url_total_og_links': url_total_og_urls,
                    'url_favicons': url_total_favicons,
                    'url_file_type': file_type,
                    'head': head,
                    'body': body
            })

        except TimeoutException:
            retry += 1
            print("      -----  Timeout, Retrying  ...... ")
            if retry >= 1:
                print("      -------    Leaving after 3 unsuccessful retry")
                break
            continue
        else:
            break
    return data_obj


def write_json(json_data, url_directory):
    """
    Create data.json in the directory
    :param json_data:
    :param url_directory:
    :return:
    """
    with open(url_directory + 'data.json', 'w') as outfile:
        json.dump(json_data, outfile)


def get_chrome_driver_instance():
    """
    initiate chrome driver instance
    :return:
    """
    chrome_options = webdriver.ChromeOptions()

    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--enable-extensions')
    chrome_options.add_argument('--enable-safebrowsing')
    chrome_options.add_argument('--enable-web-security')
    chrome_options.add_argument('disable-running-insecure-content')
    chrome_options.add_argument('disable-insecure-localhost')
    chrome_options.add_argument('--enable-client-side-phishing-detection')
    chrome_options.add_argument('safebrowsing-enable-download-protection')

    chrome_driver = webdriver.Chrome(chrome_options=chrome_options)

    return chrome_driver

    # chrome_options = webdriver.ChromeOpions()
    # chrome_options.add_argument('--headless')
    # # chrome_options.add_argument('--disable-extensions')
    # chrome_options.add_argument('--enable-safebrowsing')
    # chrome_options.add_argument('--enable-web-security')
    # # chrome_options.add_argument('--allow-running-insecure-content')
    # # chrome_options.add_argument('--allow-insecure-localhost')
    # chrome_options.add_argument('--enable-client-side-phishing-detection')
    # # chrome_options.add_argument('--safebrowsing-disable-download-protection')
    # chrome_driver = webdriver.Chrome(chrome_options=chrome_options)
    # chrome_driver.set_page_load_timeout(50)
    # chrome_driver.maximize_window()
    # return chrome_driver


def shutdown_driver(chrome_driver):
    """
    Close the chrome driver
    :param chrome_driver:
    :return:
    """
    chrome_driver.stop_client()
    chrome_driver.close()
    return True


def process_request(in_url, chrome_driver):
    """
    Main function to start extracting data from the url page
    :return:
    """
    in_url = in_url.strip(' ')
    if not in_url.endswith('/'):
        in_url += '/'

    url_dir, url_icons_dir = create_package(in_url)
    data_obj = get_url_attributes(url_dir, in_url, chrome_driver)

    print(data_obj['url_total_og_links'], data_obj['url_page_title'], data_obj['url_file_type'],
          data_obj['url_total_og_links'], data_obj['head'], data_obj['body'])

    if data_obj['url_total_og_links'] == 0 and data_obj['url_page_title'] == '' and data_obj['url_file_type'] == -1 \
            and data_obj['url_total_og_links'] == 0 and data_obj['head'] < 1 and data_obj['body'] < 1:

        verdict = "malicious"
    else:
        verdict = "Benign"
    return verdict


if __name__ == '__main__':
    """
    Program execution started from here
    """

    urls = ["http://documentary-baromet.000webhostapp.com/new/erasingin/myaccount/settings/",
            'https://cheffoodservice.gb.net/mira/Signon.php?LOB=RBGLogon&_pageLabel=56c8230c929cf977d66e4e4b4c4a87ce',
            'https://gangway.work/ru/rex/index.php',
            'https://lasserbol.com/d/directing/easyweb.td.com/waw/idp/secquestions.php',
            'http://191.96.249.41/chase/20cc6fab69cacb18215931a3c557c94d/login/?',
            'http://181.215.195.9/chase/d863a91ec20aa96ca3449881ffa76a6e/login/?',
            'https://vaisola.com/linkedin/uas/login/?email=Jackdavis@eureliosollutions.com'
            ]
    for url in urls:
        try:
            driver = get_chrome_driver_instance()
            url_verdict = process_request(url, driver)
            shutdown_driver(driver)
            print(url, url_verdict)
        except Exception as e:
            print("Exception %s in main function" % e)

    # with open("/home/shahid/projects/behaviouralClassifier/tmp/phishing_urls.csv", 'r') as f:
    #     urls = f.readlines()
    #     for url in urls:
    #         url = url.split('\n')[0]
    #         try:
    #             driver = get_chrome_driver_instance()
    #             url_verdict = process_request(url, driver)
    #             shutdown_driver(driver)
    #         except Exception as e:
    #             print("Exception %s in main function" % e)
    #         print(url, url_verdict)
