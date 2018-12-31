import base64
import hashlib
import shutil
import json
import sys
import os
from datetime import datetime
from urlparse import urlparse
import urllib2
import lxml.html
import requests
import hashlib
# import Image
from PIL import Image
from BeautifulSoup import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium import webdriver


def get_content_type(url):
    """
    A processed url needs to be input, i.e http://url.com or https://url.com
    :param url:
    :return: content type of a url
    """
    try:
        content_type = requests.head(url).headers["Content-Type"]
    except:
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
    except:
        b64_encoded = ''
    return b64_encoded


def get_url_domain(url):
    """
    Get the main domain of the url provided
    :param url:
    :return: landing domain of url(string)
    """
    try:
        if url is not None:
            parsed_uri = urlparse(url)
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    except Exception as e:
        domain = ''
    return domain

def get_page_title(driver):
    """
    Get the title of the page hit by  given url, provide processed urls with the http or https protocol
    :param url:
    :return: title (string)
    """
    # soup = BeautifulSoup(urllib2.urlopen(url))
    try:
        # title = soup.title.string
        title = driver.title
    except:
        title = ''

    return title


def get_favicons(url, directory):
    """
    Download the favicons to the directory of the domain or url - > UrlHash/Domain/icons or UrlHash/url/icons
    :param url:
    :param directory:
    :return: total no of fav icons
    """
    total_favicons = 0

    try:
        print(url)
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
            get_favicons(redirect_url, directory)

    return total_favicons


def get_favicons_selenium(driver1, directory):
    total_favicons = 0
    hash_list = []
    try:
        links = driver1.find_elements_by_tag_name('link')
    except:
        return total_favicons

    for link in links:
        try:
            rel = link.get_attribute('rel')
        except:
            pass
        if 'icon' in rel:
            href = link.get_attribute('href')

            favicon_ext = href.split('.')[-1]
            if not favicon_ext == 'svg':
                name = 'favicon_{}.ico'.format(total_favicons)
            else:
                name = 'favicon_{}.{}'.format(total_favicons, favicon_ext)

            icon = urllib2.urlopen(str(href))
            # md5_hash = img_md5_hash(icon)
            # hash_list.append(md5_hash)
            md5_hash = save_favicon_to_directory(icon, name, path=directory)
            hash_list.append(md5_hash)
            total_favicons += 1
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
    except:
        pass


def create_directory(dir_name):
    try:
        if not os.path.exists(dir_name):
            return os.makedirs(dir_name)
    except:
        print("ERROR creating %s Directory, Exiting the code" % dir_name)
        sys.exit(1)


def img_md5_hash(image):
    m = hashlib.md5(open(image.name, 'r').read())
    hash = m.hexdigest()
    return hash


def is_url_html(contentType):
    if 'text/html' in contentType:
        return True
    return False


def get_og_domains(url_og_links):
    og_domains = []
    md5_og_domains = []
    for og_url in url_og_links:
        domain = get_md5_hash(get_url_domain(og_url))
        og_domains.append(domain)
    unique_og_domains = set(og_domains)
    total_unique_og_domains = len(unique_og_domains)
    unique_og_domains = ",".join(unique_og_domains)
    return [total_unique_og_domains, unique_og_domains]


def get_og_links(driver):
    og_links = []
    total_og_links = 0
    try:
        a_tags = driver.find_elements_by_tag_name('a')
        for a_tag in a_tags:
            href = a_tag.get_attribute('href')
            og_links.append(href)
            total_og_links += 1
    except:
        pass
    return [total_og_links, og_links]


def is_title_match(url_title, domain_title):
    if url_title == domain_title:
        return True
    return False


def main():
    PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
    DATA_DIRECTORY = str(PROJ_DIR)+"/DATA/"

    # url = 'https://onedrive.live.com/download?cid=5AF1929C3A63A14A'
    url = 'https://www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un'
    domain = get_url_domain(url)
    if not url.endswith('/'):
        url += '/'
    url_hash = get_md5_hash(url)

    options = Options()
    options.set_headless(True)
    driver = webdriver.Firefox(options=options)

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

    driver.get(url)
    landing_url = driver.current_url
    landing_url_hash = get_md5_hash(landing_url)
    landing_url_base64 = get_base64(landing_url)
    url_title = get_page_title(driver)
    url_content_type = get_content_type(url)
    url_isHtml = is_url_html(url_content_type)
    url_total_og_urls, url_og_urls_list = get_og_links(driver)
    url_total_og_domains, url_og_domains = get_og_domains(url_og_urls_list)
    url_total_favicons, url_favicons = get_favicons_selenium(driver, URL_ICONS_DIRECTORY)

    driver.get(domain)
    domain_title = get_page_title(driver)
    domain_total_og_urls, domain_og_urls_list = get_og_links(driver)
    domain_total_og_domains, domain_og_domains = get_og_domains(domain_og_urls_list)
    domain_content_type = get_content_type(domain)
    domain_isHtml = is_url_html(domain_content_type)
    if domain != url:
        # driver.get(domain)
        domain_total_favicons, domain_favicons = get_favicons_selenium(driver, DOMAIN_ICONS_DIRECTORY)
    else:
        domain_total_favicons = 0
        domain_favicons = ''

    title_match = is_title_match(url_title, domain_title)

    driver.stop_client()
    driver.close()

    data_obj = {
        # Url attributes
        'url': url,
        'url_md5': get_md5_hash(url),
        'url_base64': get_base64(url),
        'url_page_title': url_title,
        'url_favicons': url_favicons,
        'url_isHtml': url_isHtml,
        'url_content_type': url_content_type,
        'url_total_favicons': url_total_favicons,
        'url_og_domains': url_og_domains,
        'url_total_og_domains': domain_total_og_domains,
        'url_total_og_urls': url_total_og_urls,

        'domain': domain,
        'domain_md5': get_md5_hash(domain),
        'domain_base64': get_base64(domain),
        'domain_page_title': domain_title,
        'domain_favicons': domain_favicons,
        'domain_isHtml': domain_isHtml,
        'domain_content_type': get_content_type(domain),
        'domain_total_favicons': domain_total_favicons,
        'domain_og_domains': domain_og_domains,
        'domain_total_og_domains': domain_total_og_domains,
        'domain_total_og_urls': domain_total_og_urls,

        'landing_url_hash': landing_url_hash,
        'landing_url_base64': landing_url_base64,
        'title_match': title_match
    }
    return data_obj


if __name__ == '__main__':
    start = datetime.now()
    data = main()
    print(data)
    print(json.dumps(data, indent=6, sort_keys=True))
    now = datetime.now()
    total_time = start-now
    print(total_time, float(total_time.microseconds/100000))
