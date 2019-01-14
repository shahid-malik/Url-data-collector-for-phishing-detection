import base64
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


def get_content_type(in_url):
    """
    A processed url needs to be input, i.e http://url.com or https://url.com
    :param in_url:
    :return: content type of a url
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
        content_type = requests.head(in_url, allow_redirects=True, verify=False, headers=headers).headers["Content-Type"]
    except:
        print("  -----  Error getting content type from url ...... ")
        content_type = 'text/html'
    return content_type


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


def get_base64(in_url):
    """
    get the base64 of the string
    :param in_url:
    :return: base64 encoded string
    """
    try:
        b64_encoded = base64.b64encode(in_url.encode())
    except Exception as exp:
        print("Error getting base64 of url or text with Exception \n %s" % exp)
        b64_encoded = ''
    return b64_encoded


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
    hash_list = []
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
                md5_hash = save_favicon_to_directory(icon, name, path=directory)
                hash_list.append(md5_hash)
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
            md5_hash = img_md5_hash(f)
            f.close()
            return md5_hash
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


def img_md5_hash(image):
    """
    get md5 hash of an image
    :param image:  image path or file
    :return: md5 hash
    """
    m = hashlib.md5(open(image.name, 'r').read())
    img_hash = m.hexdigest()
    return img_hash


def is_url_html(content_type):
    """
    check if the page on the url is an html page or not
    :param content_type:
    :return: True if url is html else False
    """
    if 'text/html' in content_type or 'text/plain' in content_type:
        return True
    return False


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
            url_content_type = get_content_type(in_url)
            url_total_og_urls, url_og_urls_list = get_og_links(chrome_driver)
            url_total_favicons = get_favicon_selenium(chrome_driver, url_directory+'icons')
            url_base64 = get_base64(in_url)
            page_title = get_page_title(chrome_driver)
            file_type = get_file_type(in_url)
            is_html = is_url_html(url_content_type)

            data_obj.update({
                    'url_md5': url_hash,
                    'url_page_title': page_title,
                    'url_content_type': url_content_type,
                    'url_total_og_links': url_total_og_urls,
                    'url_favicons': url_total_favicons,
                    'url_file_type': file_type,
                    'url_isHtml': is_html,
                    'head': head,
                    'body': body
            })
            if 'https' in str(in_url):
                protocol = 'https'
            else:
                protocol = 'http'
            json_data = {'url_base64': url_base64, 'protocol': protocol, 'title': page_title}
            write_json(json_data, url_directory)
        except TimeoutException:
            retry += 1
            print("      -----  Timeout, Retrying  ...... ")
            if retry >= 3:
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
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--enable-safebrowsing')
    chrome_options.add_argument('--enable-web-security')
    # chrome_options.add_argument('--allow-running-insecure-content')
    # chrome_options.add_argument('--allow-insecure-localhost')
    chrome_options.add_argument('--enable-client-side-phishing-detection')
    # chrome_options.add_argument('--safebrowsing-disable-download-protection')
    chrome_driver = webdriver.Chrome(chrome_options=chrome_options)
    chrome_driver.set_page_load_timeout(50)
    chrome_driver.maximize_window()
    return chrome_driver


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
    if 'text' in data_obj['url_content_type'] and data_obj['url_total_og_links'] == 0 and data_obj['url_isHtml'] and \
            data_obj['url_page_title'] == '' and data_obj['url_file_type'] == -1 and \
            data_obj['url_total_og_links'] == 0 and data_obj['head'] < 1 and data_obj['body'] < 1:

        verdict = "malicious"
    else:
        verdict = "Benign"
    return verdict


if __name__ == '__main__':
    """
    Program execution started from here
    """

    with open("/home/shahid/projects/behaviouralClassifier/tmp/phishing_urls.csv", 'r') as f:
        urls = f.readlines()
        for url in urls:
            url = url.split('\n')[0]
            try:
                status = urllib2.urlopen(url).code
                if status == 200:
                    try:
                        driver = get_chrome_driver_instance()
                        url_verdict = process_request(url, driver)
                        shutdown_driver(driver)
                    except Exception as e:
                        print("Exception %s in main function" % e)
                else:
                    url_verdict = -1
            except:
                url_verdict =- 1
            print(url, url_verdict)
