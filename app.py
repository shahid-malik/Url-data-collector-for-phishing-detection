import base64
import math
# import hashlib
# import shutil
import json
import sys
import os
from datetime import datetime
from urlparse import urlparse
import urllib2
import requests
import hashlib
import magic
# import mimetypes
import urllib
# import Image
from BeautifulSoup import BeautifulSoup
# from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from lib import api, db
from selenium.common.exceptions import TimeoutException
requests.packages.urllib3.disable_warnings()


def get_content_type(url):
    """
    A processed url needs to be input, i.e http://url.com or https://url.com
    :param url:
    :return: content type of a url
    """
    try:
        content_type = requests.head(url, allow_redirects=True, verify=False).headers["Content-Type"]
    except Exception as e:
        print("Error getting favicon from landing page")
        content_type = ''
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
    except Exception as e:
        print("Error getting base64 of url or text with Exception \n %s" % e)
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
    except Exception as e:
        print("Exception in getting domain from given url with exception %s" % e)
        pass
    return domain, path


def get_page_title(driver):
    """
    Get the title of the page hit by  given url, provide processed urls with the http or https protocol
    :param driver:
    :return: title (string)
    """
    # soup = BeautifulSoup(urllib2.urlopen(url))
    try:
        # title = soup.title.string
        title = driver.title.encode('ascii', 'replace')
    except Exception as e:
        print("Error while extracting title from landing page with Exception \n %s" % e)

        title = ''

    return title


def get_favicon(url, directory):
    """
    Download the favicons to the directory of the domain or url - > UrlHash/Domain/icons or UrlHash/url/icons
    :param url:
    :param directory:
    :return: total no of fav icons
    """
    total_favicons = 0

    try:
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page.read())
        # favicon_links = soup.findAll("link", {'rel': ['icon', 'mask-icon', 'apple-touch-icon', 'shortcut icon',
        #                                               'apple-touch-icon-precomposed']})
        favicon_links = soup.findAll("link", {'rel': ['icon', 'mask-icon', 'apple-touch-icon', 'shortcut icon',
                                                      'apple-touch-icon-precomposed']})
        for favicon in favicon_links:
            try:
                icon = urllib2.urlopen(favicon['href'])
            except:
                raw_url = favicon['href']
                icon_url = 'http://'+raw_url[raw_url.find('www'):]
                icon = urllib2.urlopen(icon_url)

            favicon_ext = favicon['href'].split('.')[-1]
            if not favicon_ext == 'svg':
                name = 'favicon_{}.ico'.format(total_favicons)
            else:
                name = 'favicon_{}.{}'.format(total_favicons, favicon_ext)
            save_favicon_to_directory(icon, name, path=directory)
            total_favicons += 1
    except:
        if requests.head(url).status_code == 302:
            # redirect_url = requests.head(url).next.path_url
            redirect_url = requests.head(url, allow_redirects=True).url
            get_favicon(redirect_url, directory)

    return total_favicons


def get_favicon_selenium(driver1, directory):
    """
    Get favicons of the url given,
    :param driver1: selenium driver with the url
    :param directory: directory to store the favicon
    :return: total favicon and list of favicon
    """
    total_favicons = 0
    hash_list = []
    rel = ""
    try:
        links = driver1.find_elements_by_tag_name('link')
    except Exception as e:
        print("Error getting favicon from landing page with Exception \n %s" % e)
        return total_favicons

    for link in links:
        try:
            rel = link.get_attribute('rel')
        except Exception as e:
            print("Error getting favicon links from landing page with Exception \n %s" % e)
            pass

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
            except Exception as e:
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
    name = path+name
    try:
        with open(name, "wb") as f:
            f.write(icon.read())
            md5_hash = img_md5_hash(f)
            f.close()
            return md5_hash
    except Exception as e:
        print("Error while saving favicon to the directory \n %s" % e)

        pass


def create_directory(dir_name):
    """
    Create packages directory on the local machine
    :param dir_name: directory path
    :return:
    """
    try:
        if not os.path.exists(dir_name):
            return os.makedirs(dir_name)
    except Exception as e:
        print("ERROR creating %s Directory, Exiting the code" % dir_name, " | with Exception %s" % e)
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
    # md5_og_domains = []
    for og_url in url_og_links:
        domain = get_md5_hash(get_url_domain_n_path(og_url)[0])
        og_domains.append(domain)
    unique_og_domains = set(og_domains)
    total_unique_og_domains = len(unique_og_domains)
    unique_og_domains = ",".join(unique_og_domains)
    return [total_unique_og_domains, unique_og_domains]


def get_og_links(driver):
    """
    get outgoing links for landing page of the url
    :param driver: selenium url driver
    :return: total outgoing links and list of og links
    """
    og_links = []
    total_og_links = 0
    try:
        a_tags = driver.find_elements_by_tag_name('a')
        for a_tag in a_tags:
            href = a_tag.get_attribute('href')
            og_links.append(href)
            total_og_links += 1
    except Exception as e:
        print("Exceptions in getting outgoing links from the page %s" % e)
        pass
    return [total_og_links, og_links]


def is_title_match(url_title, domain_title):
    """
    If title on the url and title on the domain is same
    :param url_title:
    :param domain_title:
    :return:
    """
    if url_title == domain_title:
        return True
    return False


def get_file_type(url):
    """
    Get the file type of the landing page on url
    :param url:
    :return:
    """
    mime = magic.Magic(mime=True)
    output = "output"
    try:
        urllib.urlretrieve(url, output)
        mimes = mime.from_file(output)
        return mimes
    except:
        pass


def get_entropy(string, base=2.0):
    dct = dict.fromkeys(list(string))
    pkvec = [float(string.count(c)) / len(string) for c in dct]
    H = -sum([pk * math.log(pk) / math.log(base) for pk in pkvec])
    return H


def main():
    """
    Main function to start extracting data from the url page
    :return:
    """
    PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
    DATA_DIRECTORY = str(PROJ_DIR)+"/DATA/"

    # url = 'https://onedrive.live.com/download?cid=5AF1929C3A63A14A'
    # url = 'https://www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un'
    # url = 'http://www.americanshipper.com/'
    # url = 'http://media.mtvnservices.com/edge/bento/miso.1.4.17.swf'
    # url = 'https://chromedriver.storage.googleapis.com/2.45/chromedriver_linux64.zip'
    # url = 'https://chromedriver.storage.googleapis.com/2.45/chromedriver_mac64.zip'
    # url = 'http://mahdijamnqatar.com/home/D7298292/mao'
    # url = 'https://www.nemanjaarnautovicinc.com/ZT0iZW1haWwiIHJlcXVpcmVkIGNsYXNzPSJmb3JtLWNvbnRyb2wiIGlkPSJlbWFpbCIgbmFtZT0iZW1haWwiIHBsYWNlaG9sZGVyPSIiIHZhbHV/buttonabsa.png'
    url = 'http://seemg.ir/wp-snapshots/US/Clients_Messages/122018/'
    # url = api.get_url()
    url_hash = get_md5_hash(url)
    domain_title = ''
    url_title = ''
    print(" ***** Processing %s  ***** " % url)
    domain = get_url_domain_n_path(url)[0]
    path = get_url_domain_n_path(url)[1]
    # if not url.endswith('/'):
    #     url += '/'

    print("  -----  Starting headless browser   ...... ")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-safebrowsing')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--allow-insecure-localhost')
    chrome_options.add_argument('--disable-client-side-phishing-detection')
    chrome_options.add_argument('--safebrowsing-disable-download-protection')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_page_load_timeout(20)

    PACKAGE_DIRECTORY = DATA_DIRECTORY + url_hash+'/'
    DOMAIN_DIRECTORY = PACKAGE_DIRECTORY + 'domain/'
    DOMAIN_ICONS_DIRECTORY = DOMAIN_DIRECTORY + 'icons/'
    URL_DIRECTORY = PACKAGE_DIRECTORY + 'url/'
    URL_ICONS_DIRECTORY = URL_DIRECTORY + 'icons/'

    create_directory(PACKAGE_DIRECTORY)
    create_directory(DOMAIN_DIRECTORY)
    create_directory(DOMAIN_ICONS_DIRECTORY)
    create_directory(URL_DIRECTORY)
    create_directory(URL_ICONS_DIRECTORY)
    print("  -----  Package Created  ...... ")
    retry = 0
    while True:
        try:
            driver.get(url)
            url_entropy = get_entropy(url)
            landing_url = driver.current_url
            landing_url_hash = get_md5_hash(landing_url)
            landing_url_base64 = get_base64(landing_url)
            url_title = get_page_title(driver)
            url_content_type = get_content_type(url)
            url_total_og_urls, url_og_urls_list = get_og_links(driver)
            url_total_og_domains, url_og_domains = get_og_domains(url_og_urls_list)
            url_total_favicon, url_favicon = get_favicon_selenium(driver, URL_ICONS_DIRECTORY)
            url_file_type = get_file_type(url)
            url_isHtml = is_url_html(url_content_type)
        except TimeoutException:
            retry += 1
            print("  -----  Timeout, Retrying  ...... ")
            if retry >= 1:
                print("  -------    Breaking the loop after 2 unsuccessful retry")
                break
            continue
        else:
            break
    print("  -----  Url Attributes Done  ...... ")


    retry = 0
    while True:
        try:
            driver.get(domain)
            domain_entropy = get_entropy(domain)
            domain_title = get_page_title(driver)
            domain_total_og_urls, domain_og_urls_list = get_og_links(driver)
            domain_total_og_domains, domain_og_domains = get_og_domains(domain_og_urls_list)
            domain_content_type = get_content_type(domain)
            domain_isHtml = is_url_html(domain_content_type)
            domain_file_type = get_file_type(domain)
            if domain != url:
                domain_total_favicons, domain_favicons = get_favicon_selenium(driver, DOMAIN_ICONS_DIRECTORY)
            else:
                domain_total_favicons = url_total_favicon
                domain_favicons = url_favicon
        except TimeoutException:
            retry += 1
            print("  -----  Timeout, Retrying  ......")
            if retry >= 1:
                print("  -------    Breaking the loop after 2 unsuccessful retry")
                break
            continue
        else:
            break

    print("  -----  Domain Attributes Done ...... ")
    title_match = is_title_match(url_title, domain_title)
    driver.stop_client()
    driver.close()
    print("  -----  Stop Chrome headless  ......  ")

    data_obj = {
        # Url attributes
        'url': url,
        'url_md5': get_md5_hash(url),
        'url_base64': get_base64(url),
        'url_page_title': url_title,
        'url_favicons': url_favicon,
        'url_isHtml': url_isHtml,
        'url_content_type': url_content_type,
        'url_total_favicon': url_total_favicon,
        'url_og_domains': url_og_domains,
        'url_total_og_domains': domain_total_og_domains,
        'url_total_og_links': url_total_og_urls,
        'url_is_html': url_isHtml,
        'url_file_type': url_file_type,
        'url_entropy': url_entropy,

        'domain': domain,
        'domain_md5': get_md5_hash(domain),
        'domain_base64': get_base64(domain),
        'domain_page_title': domain_title,
        'domain_favicons': domain_favicons,
        'domain_isHtml': domain_isHtml,
        'domain_content_type': get_content_type(domain),
        'domain_total_favicon': domain_total_favicons,
        'domain_og_domains': domain_og_domains,
        'domain_total_og_domains': domain_total_og_domains,
        'domain_total_og_links': domain_total_og_urls,
        'domain_file_type': domain_file_type,
        'domain_entropy': domain_entropy,
        'landing_url_hash': landing_url_hash,
        'landing_url_base64': landing_url_base64,
        'title_match': title_match,
        'uri_length': len(path),
        'url_length': len(url)
    }
    return data_obj


if __name__ == '__main__':
    DATA_TABLE = "package_features"

    while(1):
        try:
            start = datetime.now()
            data = main()
            # print(json.dumps(data, indent=6, sort_keys=True))
            db.insert_data(DATA_TABLE, data)
            total_time = start-datetime.now()
            print("  -----  Total Time Spent  %s ......" % float(total_time.microseconds/100000))
        except:
            pass
