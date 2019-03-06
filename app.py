import base64
import math
import datetime
import time
import json
import sys
import os
from datetime import datetime
from urlparse import urlparse
import urllib2
import requests
import hashlib
import magic
import socket
import urllib
from selenium import webdriver
from lib import api, db, html2txt
from PIL import Image
from selenium.common.exceptions import TimeoutException

requests.packages.urllib3.disable_warnings()
reload(sys)
sys.setdefaultencoding('utf8')

# Set the default timeout in seconds

timeout = 50
socket.setdefaulttimeout(timeout)


def get_content_type(url):
    """
    A processed url needs to be input, i.e http://url.com or https://url.com
    :param url:
    :return: content type of a url
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
        content_type = requests.head(url, allow_redirects=True, timeout=5, verify=False, headers=headers).headers["Content-Type"]
    except requests.exceptions.Timeout:
        print("  -----  Error getting content type from url ...... ")
        content_type = 'text/html'
    return content_type


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


def get_base64(url):
    """
    get the base64 of the string
    :param url:
    :return: base64 encoded string
    """
    try:
        b64_encoded = base64.b64encode(url.encode())
    except Exception as exp:
        print("Error getting base64 of url or text with Exception \n %s" % exp)
        b64_encoded = ''
    return b64_encoded


def get_url_domain_n_path(url):
    """
    Get the main domain of the url provided
    :param url:
    :return: landing domain of url(string)
    """
    domain = ''
    path = ''
    try:
        if url is not None:
            parsed_uri = urlparse(url)
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            path = parsed_uri.path
    except Exception as exp:
        print("Exception in getting domain from given url with exception %s" % exp)
    return domain, path


def get_page_title(chrome_driver):
    """
    Get the title of the page hit by  given url, provide processed urls with the http or https protocol
    :param chrome_driver:
    :return: title (string)
    """
    try:
        # title = soup.title.string
        title = chrome_driver.title.decode('utf-8')
        title = title.replace("'", "''")
    except Exception as exp:
        title = ''
        print("Error while extracting title from landing page with Exception \n %s" % exp)
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
                # md5_hash = img_md5_hash(icon)
                # hash_list.append(md5_hash)
                md5_hash = save_favicon_to_directory(icon, name, path=directory)
                hash_list.append(md5_hash)
                total_favicons += 1
            except:
                pass

    hash_list = ",".join(hash_list)
    return [total_favicons, hash_list]


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


def get_og_domains(url_og_links):
    """
    Get all the domain associated with outgoing links in a single page
    :param url_og_links: list of outgoing urls
    :return: total outgoing domains and list of outgoing domains
    """
    og_domains = []
    for og_url in url_og_links:
        domain = get_md5_hash(get_url_domain_n_path(og_url)[0])
        og_domains.append(domain)
    unique_og_domains = set(og_domains)
    total_unique_og_domains = len(unique_og_domains)
    unique_og_domains = ",".join(unique_og_domains)
    return [total_unique_og_domains, unique_og_domains]


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


def is_title_match(url_title, domain_title):
    """
    If title on the url and title on the domain is same
    :param url_title:
    :param domain_title:
    :return:
    """
    if url_title == domain_title:
        return 1
    return 0


def get_file_type(url):
    """
    Get the file type of the landing page on url
    :param url:
    :return:
    """
    mime = magic.Magic(mime=True)
    output = "tmp/output"
    try:
        status = urllib2.urlopen(url).code
        if status:
            urllib.urlretrieve(url, output)
            mimes = mime.from_file(output)
            return mimes
    except Exception as ex:
        return -1


def get_entropy(string, base=2.0):
    """
    Get the entropy, Entropy measures the complexity of the url or domain
    :param string:
    :param base:
    :return:
    """
    dct = dict.fromkeys(list(string))
    pkvec = [float(string.count(c)) / len(string) for c in dct]
    H = -sum([pk * math.log(pk) / math.log(base) for pk in pkvec])
    return H


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


def fullpage_screenshot(directory_path, chrome_driver):
    file = directory_path + "screenshot.png"

    try:
        total_width = chrome_driver.execute_script("return document.body.offsetWidth")
        total_height = chrome_driver.execute_script("return document.body.parentNode.scrollHeight")
        viewport_width = chrome_driver.execute_script("return document.body.clientWidth")
        viewport_height = chrome_driver.execute_script("return window.innerHeight")
        rectangles = []

        i = 0
        while i < total_height:
            ii = 0
            top_height = i + viewport_height
            if top_height > total_height:
                top_height = total_height
            while ii < total_width:
                top_width = ii + viewport_width
                if top_width > total_width:
                    top_width = total_width
                rectangles.append((ii, i, top_width, top_height))
                ii = ii + viewport_width
            i = i + viewport_height
        stitched_image = Image.new('RGB', (total_width, total_height))
        previous = None
        part = 0

        for rectangle in rectangles:
            if not previous is None:
                try:
                    chrome_driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
                    time.sleep(0.2)
                    chrome_driver.execute_script(
                        "document.getElementById('topnav').setAttribute('style', 'position: absolute; top: 0px;');")
                    time.sleep(0.2)
                except:
                    pass
                time.sleep(0.2)
            file_name = "part_{0}.png".format(part)
            chrome_driver.get_screenshot_as_file(file_name)
            screenshot = Image.open(file_name)
            if rectangle[1] + viewport_height > total_height:
                offset = (rectangle[0], total_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])
            stitched_image.paste(screenshot, offset)
            del screenshot
            os.remove(file_name)
            part = part + 1
            previous = rectangle
        stitched_image.save(file)
        return True
    except:
        pass


def create_package(data_directory, url):
    """
    Create a package with domain and url directories
    :param data_directory:
    :param url:
    :return:
    """
    url_hash = get_md5_hash(url)
    domain = get_url_domain_n_path(url)[0]
    DOMAIN_ICONS_DIRECTORY = ''
    DOMAIN_DIRECTORY = ''
    PACKAGE_DIRECTORY = data_directory + url_hash + '/'
    create_directory(PACKAGE_DIRECTORY)
    if not url.endswith('/'):
        url += '/'

    if url == domain:
        URL_DIRECTORY = PACKAGE_DIRECTORY + 'url/'
        URL_ICONS_DIRECTORY = URL_DIRECTORY + 'icons/'
        create_directory(URL_DIRECTORY)
        create_directory(URL_ICONS_DIRECTORY)
    else:
        URL_DIRECTORY = PACKAGE_DIRECTORY + 'url/'
        URL_ICONS_DIRECTORY = URL_DIRECTORY + 'icons/'
        create_directory(URL_DIRECTORY)
        create_directory(URL_ICONS_DIRECTORY)

        DOMAIN_DIRECTORY = PACKAGE_DIRECTORY + 'domain/'
        DOMAIN_ICONS_DIRECTORY = DOMAIN_DIRECTORY + 'icons/'
        create_directory(DOMAIN_DIRECTORY)
        create_directory(DOMAIN_ICONS_DIRECTORY)
    print("  -----  Package Created  ...... ")
    return URL_DIRECTORY, URL_ICONS_DIRECTORY, DOMAIN_DIRECTORY, DOMAIN_ICONS_DIRECTORY


def is_favicon_match(url_favicon, domain_favicon):
    """
    Find if url favicon and domain favicon matched
    :return:
    """
    url_favicon_set = set(url_favicon.split(','))
    domain_favicon_set = set(domain_favicon.split(','))
    if set(url_favicon_set) & set(domain_favicon_set):
        return 1
    return 0


def get_domain_attributes(domain_icons_directory, domain_directory, domain, chrome_driver):
    """
    Get domain attributes.csv
    :param domain_icons_directory:
    :param domain_directory:
    :param domain:
    :param chrome_driver:
    :return:
    """

    data_obj = {}
    retry = 0
    while True:
        try:
            chrome_driver.get(domain)

            # create_screenshot(domain_directory, chrome_driver)
            fullpage_screenshot(domain_directory, chrome_driver)
            file_path = save_html(domain_directory, chrome_driver)
            html2txt.text_from_html(domain_directory, file_path)

            domain_total_og_urls, domain_og_urls_list = get_og_links(chrome_driver)
            domain_total_og_domains, domain_og_domains = get_og_domains(domain_og_urls_list)
            domain_content_type = get_content_type(domain)
            domain_total_favicons, domain_favicons = get_favicon_selenium(chrome_driver, domain_icons_directory)

            data_obj['domain_md5'] = get_md5_hash(domain)
            data_obj['domain_base64'] = get_base64(domain)
            data_obj['domain_entropy'] = get_entropy(domain)
            data_obj['domain_page_title'] = get_page_title(chrome_driver)
            data_obj['domain'] = domain
            data_obj['domain_favicons'] = domain_favicons
            data_obj['domain_content_type'] = domain_content_type
            data_obj['domain_total_favicon'] = domain_total_favicons
            data_obj['domain_og_domains'] = domain_og_domains
            data_obj['domain_total_og_domains'] = domain_total_og_domains
            data_obj['domain_total_og_links'] = domain_total_og_urls
            data_obj['domain_entropy'] = get_entropy(domain)
            data_obj['domain_isHtml'] = is_url_html(domain_content_type)
            data_obj['domain_file_type'] = get_file_type(domain)

            if 'https' in str(domain):
                protocol = 'https'
            else:
                protocol = 'http'
            json_data = {'url_base64': data_obj['domain_base64'], 'protocol': protocol,
                         'title': data_obj['domain_page_title']}
            write_json(json_data, domain_directory)

            print("  -----  Domain Attributes Done ...... ")
        except TimeoutException:
            retry += 3
            print("  -----  Timeout, Retrying  ......")
            if retry >= 1:
                print("      -------    Leaving after 3 unsuccessful retry")
                break
            continue
        else:
            break
    return data_obj


def get_url_attributes(url_icon_directory, url_directory, url, chrome_driver):
    """
    Get attributes.csv from url
    :param url_icon_directory:
    :param url_directory:
    :param url:
    :param chrome_driver:
    :return:
    """
    retry = 0
    data_obj = {}
    url_hash = get_md5_hash(url)
    while True:
        try:
            chrome_driver.get(url)

            # create_screenshot(url_directory, chrome_driver)
            fullpage_screenshot(url_directory, chrome_driver)

            file_path = save_html(url_directory, chrome_driver)
            html2txt.text_from_html(url_directory, file_path)

            landing_url = chrome_driver.current_url
            landing_url_hash = get_md5_hash(landing_url)
            landing_url_base64 = get_base64(landing_url)
            url_content_type = get_content_type(url)
            url_total_og_urls, url_og_urls_list = get_og_links(chrome_driver)
            url_total_og_domains, url_og_domains = get_og_domains(url_og_urls_list)
            url_total_favicons, url_favicons = get_favicon_selenium(chrome_driver, url_icon_directory)
            url_base64 = get_base64(url)
            url_entropy = get_entropy(url)
            page_title = get_page_title(chrome_driver)
            file_type = get_file_type(url)
            is_html = is_url_html(url_content_type)

            data_obj['url'] = url
            data_obj['url_md5'] = url_hash
            data_obj['url_base64'] = url_base64
            data_obj['url_entropy'] = url_entropy
            data_obj['url_page_title'] = page_title
            data_obj['url_content_type'] = url_content_type
            data_obj['url_total_og_links'] = url_total_og_urls
            data_obj['url_og_domains'] = url_og_domains
            data_obj['url_total_og_domains'] = url_total_og_domains
            data_obj['url_favicons'] = url_favicons
            data_obj['url_total_favicon'] = url_total_favicons
            data_obj['url_file_type'] = file_type
            data_obj['url_isHtml'] = is_html
            data_obj['landing_url_hash'] = landing_url_hash
            data_obj['landing_url_base64'] = landing_url_base64
            data_obj['url_length'] = len(url)
            data_obj['total_at_the_rate'] = url.count('@')
            if 'https' in str(url):
                protocol = 'https'
            else:
                protocol = 'http'
            json_data = {'url_base64': url_base64, 'protocol': protocol, 'title': page_title}
            write_json(json_data, url_directory)

            print("  -----  Url Attributes Done  ...... ")
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


def get_current_time():
    """
    Get current time in the (year-month-date Hour-minute-Second) format
    :return:
    """
    ts = time.time()
    timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


def get_chrome_driver_instance():
    """
    initiate chrome driver instance
    :return:
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-safebrowsing')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--allow-insecure-localhost')
    chrome_options.add_argument('--disable-client-side-phishing-detection')
    chrome_options.add_argument('--safebrowsing-disable-download-protection')
    chrome_driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options)
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


def start_processing_url(data_directory, chrome_driver):
    """
    Main function to start extracting data from the url page
    :param data_directory:
    :param chrome_driver:
    :return:
    :return:
    """

    data_obj = {}
    domain_attributes = {}
    url = api.get_url()
    url = 'https://mega.nz/#!KpRAFK6Q!dRtfzwmJl9VF-6ScHduEt06788pwP--EQmJ8qUf2cUY/'
    if not url:
        url = api.get_url()
    url = url.strip(' ')
    if not url.endswith('/'):
        url += '/'
    url_hash = get_md5_hash(url)

    print(" ***** Processing %s  ***** " % url)
    print("  -----  Start Time   %s ......" % start_time)
    print("  -----  Package_hash: %s" % url_hash)
    domain, path = get_url_domain_n_path(url)
    url_directory, url_icons_directory, domain_directory, domain_icons_directory = create_package(data_directory, url)
    url_attributes = get_url_attributes(url_icons_directory, url_directory, url, chrome_driver)

    if url != domain:
        domain_attributes = get_domain_attributes(url_icons_directory, url_directory, domain, chrome_driver)
    elif url_attributes:
        domain_attributes['domain'] = domain
        domain_attributes['domain_md5'] = url_hash
        domain_attributes['domain_base64'] = url_attributes['url_base64']
        domain_attributes['domain_entropy'] = url_attributes['url_entropy']
        domain_attributes['domain_page_title'] = url_attributes['url_page_title']
        domain_attributes['domain_favicons'] = url_attributes['url_favicons']
        domain_attributes['domain_content_type'] = url_attributes['url_content_type']
        domain_attributes['domain_total_favicon'] = url_attributes['url_total_favicon']
        domain_attributes['domain_og_domains'] = url_attributes['url_og_domains']
        domain_attributes['domain_total_og_domains'] = url_attributes['url_total_og_domains']
        domain_attributes['domain_total_og_links'] = url_attributes['url_total_og_links']
        domain_attributes['domain_entropy'] = url_attributes['url_entropy']
        domain_attributes['domain_isHtml'] = url_attributes['url_isHtml']
        domain_attributes['domain_file_type'] = url_attributes['url_file_type']
        domain_attributes['is_favicon_match'] = 0
        print("  -----  Domain Attributes Done ...... ")

    data_obj.update(url_attributes)
    data_obj.update(domain_attributes)
    if url_attributes or domain_attributes:
        title_match = is_title_match(data_obj['domain_page_title'], data_obj['url_page_title'])
        data_obj['is_favicon_match'] = is_favicon_match(domain_attributes['domain_favicons'],
                                                        url_attributes['url_favicons'])
        data_obj['title_match'] = title_match

    data_obj['uri_length'] = len(path)
    data_obj['timestamp'] = get_current_time()

    return data_obj


if __name__ == '__main__':
    """
    Program execution started from here
    """

    PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
    DATA_DIRECTORY = str(PROJ_DIR) + "/DATA/"
    while True:
        try:
            start_time = datetime.now()
            driver = get_chrome_driver_instance()
            data = start_processing_url(DATA_DIRECTORY, driver)
            if len(data.keys()) > 5:
                db.insert_data(data)
            else:
                print("  -----  Skipping DB entry due to data issue ......")
            shutdown_driver(driver)

            total_time = start_time - datetime.now()
            print("  -----  Total Time Spent  %s ......" % float(total_time.microseconds / 100000))
        except Exception as e:
            print("Exception %s in main function" % e)
