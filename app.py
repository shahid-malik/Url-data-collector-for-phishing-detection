import base64
import hashlib
import shutil
import sys
import os
from datetime import datetime
from urlparse import urlparse
import urllib2
import lxml.html
import requests
from BeautifulSoup import BeautifulSoup
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
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain


def get_page_title(url):
    """
    Get the title of the page hit by  given url, provide processed urls with the http or https protocol
    :param url:
    :return: title (string)
    """
    soup = BeautifulSoup(urllib2.urlopen(url))
    try:
        title = soup.title.string
    except:
        title = ''

    return title


# def get_favicons(url):
#     HEADERS = {
#         'User-Agent': 'urllib2 (Python %s)' % sys.version.split()[0],
#         'Connection': 'close',
#     }
#
#     path = 'favicon.ico'
#     alt_icon_path = 'alticon.ico'
#
#     if not url.endswith('/'):
#         url += '/'
#
#     request = urllib2.Request(url+'favicon.ico', headers=HEADERS)
#     try:
#         icon = urllib2.urlopen(request).read()
#     except:
#         request = urllib2.Request(url, headers=HEADERS)
#         try:
#             content = urllib2.urlopen(request).read(4096)
#         except:
#             shutil.copyfile(alt_icon_path, path)
#             return
#         icon_path = lxml.html.fromstring(x).xpath(
#             '//link[@rel="icon" or @rel="shortcut icon"]/@href'
#         )
#         if icon_path:
#             request= urllib2.Request(url+icon_path[:1], headers=HEADERS)
#             try:
#                 icon = urllib2.Request(request).read()
#             except(urllib2.HTTPError, urllib2.URLError):
#                 shutil.copyfile(alt_icon_path, path)
#                 return
#     open(path, 'wb').write(icon)



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
    links = driver1.find_elements_by_tag_name('link')
    for link in links:
        rel = link.get_attribute('rel')
        if 'icon' in rel:
            href = link.get_attribute('href')

            favicon_ext = href.split('.')[-1]
            if not favicon_ext == 'svg':
                name = 'favicon_{}.ico'.format(total_favicons)
            else:
                name = 'favicon_{}.{}'.format(total_favicons, favicon_ext)
            icon = urllib2.urlopen(str(href))
            save_favicon_to_directory(icon, name, path=directory)
            total_favicons += 1
    return total_favicons


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
    except:
        pass


def create_directory(dir_name):
    try:
        if not os.path.exists(dir_name):
            return os.makedirs(dir_name)
    except:
        print("ERROR creating %s Directory, Exiting the code" % dir_name)
        sys.exit(1)


def main():
    PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
    DATA_DIRECTORY = str(PROJ_DIR)+"/DATA/"

    url = 'https://onedrive.live.com/download?cid=5AF1929C3A63A14A'
    url_hash = get_md5_hash(url)

    driver = webdriver.Firefox()
    driver.get(url)

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

    print(get_favicons_selenium(driver, URL_ICONS_DIRECTORY))
    domain = get_url_domain(url)
    driver.get(domain)
    print(get_favicons_selenium(driver, DOMAIN_ICONS_DIRECTORY))

    # data_obj = {
    #     # Url attributes
    #     'url': url,
    #     'url_content_type': get_content_type(url),
    #     'url_md5': get_md5_hash(url),
    #     'url_base64': get_base64(url),
    #     'url_page_title': get_page_title(url),
    #     # domain attributes
    #     'domain': domain,
    #     'domain_content_type': get_content_type(domain),
    #     'domain_md5': get_md5_hash(domain),
    #     'domain_base64': get_base64(domain),
    #     'domain_page_title': get_page_title(domain)
    # }
    # return data_obj

if __name__ == '__main__':
    start = datetime.now()
    data = main()
    # print(json.dumps(data, indent=6, sort_keys=True))
    now = datetime.now()
    total_time = start-now
    print(total_time, float(total_time.microseconds/100000))
