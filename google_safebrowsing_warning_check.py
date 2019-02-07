import os
import sys
import urllib2
import requests
import ssl
import subprocess
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup

requests.packages.urllib3.disable_warnings()
reload(sys)
sys.setdefaultencoding('utf8')

ssl._create_default_https_context = ssl._create_unverified_context


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


def get_url_domain(input_url):
    """
    Get the main domain of the url provided
    :param input_url:
    :return: landing domain of url(string)
    """
    domain = ''
    try:
        if input_url is not None:
            parsed_uri = urlparse(input_url)
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    except Exception as exp:
        print("Exception in getting domain from given url with exception %s" % exp)
    return domain


def get_verdict(verdict_file):
    """
    Read the verdict from verdict file in tmp folder generated by the google safe browsing api
    :param verdict_file:
    :return:
    """
    verdict_list = []
    with open(verdict_file, 'r') as in_file:
        lines = in_file.readlines()
        for line in lines:
            verdict_list.append(line.split(',')[1].rstrip())
    if 'Malicious' in verdict_list:
        return 'Malicious'
    else:
        return 'Benign'


def process_request_gsb(input_url, input_urls_file):
    """
    Get all the outgoing links of the page hit by  given url, provide processed urls with the http or https protocol
    :param input_urls_file: 
    :param input_url:
    :return: list of urls verdict file
    """
    soup = BeautifulSoup(urllib2.urlopen(input_url))
    domain = get_url_domain(input_url)
    try:
        url_list = set()
        ahrefs = soup.findAll('a')
        iframes = soup.findAll('iframe')
        inputs = soup.findAll('input')
        imgs = soup.findAll('img')
        links = soup.findAll('link')

        for ahref in ahrefs:
            try:
                ahref_url = str(ahref['href'])
                if not ahref_url.startswith('http'):
                    ahref_url = str(input_url + ahref_url)
                url_list.add(ahref_url)
            except Exception as exp:
                print("exception extracting link from <a> tag", exp)

        for link in links:
            try:
                link_url = str(link['href'])
                if not link_url.startswith('http'):
                    link_url = str(input_url + link_url)
                url_list.add(link_url)
            except Exception as exp:
                print("exception extracting link from <link> tag", exp)

        for iframe in iframes:
            try:
                iframe_url = str(iframe['src'])
                if not iframe_url.startswith('http'):
                    iframe_url = str(input_url + iframe_url)
                url_list.add(iframe_url)
            except Exception as exp:
                print("exception extracting link from <iframe> tag", exp)

        for input in inputs:
            try:
                i_url = str(input['src'])
                if not i_url.startswith('http'):
                    i_url = str(input_url + i_url)
                url_list.add(i_url)
            except:
                pass
                # print("exception extracting link from <input> tag", exp)

        for img in imgs:
            try:
                img_url = str(img['src'])
                if not img_url.startswith('http'):
                    img_url = str(input_url + img_url)
                url_list.add(img_url)
            except Exception as exp:
                print("exception extracting link from <img>", exp)

        url_list.add(domain)
        with open(input_urls_file, 'w') as outfile:
            outfile.writelines("url\n")
            outfile.writelines(["{}\n".format(item) for item in url_list])
    except Exception as exp:
        print("Error while extracting title from landing page with Exception \n %s" % exp)


def run(input_urls_file, verdict_file):
    """
    run the google safe browsing bash command to get the verdict against each url list in file tmp/urls.csv
    :param input_urls_file:
    :param verdict_file:
    :return:
    """
    command = "gsb-check.py --urls %s --host localhost --user root --password 12345678 --db-name " \
              "PrefixCache --keys ~/projects/gsb_keys.txt --output %s" % (input_urls_file, verdict_file)
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
    except Exception as exp:
        print(exp)


if __name__ == '__main__':
    """
    Program execution started from here
    """
    curr_dir = os.path.dirname(os.path.realpath(__file__))

    urls = [
        'https://gangway.work/ru/rex/index.php',
        'https://bankamericaaof.cf/acc/home/login/index.php',
        'https://agropecuariaelcimarron.co/wp-content/uploads/cache/transfer/cbbce62a2a435703bc54fc084ecb28ed/'
    ]
    urls_file = curr_dir + '/tmp/' + 'urls.csv'
    urls_verdict_file = curr_dir + '/tmp/' + 'urls_verdict.csv'

    for url in urls:
        try:
            process_request_gsb(url, urls_file)

            run(urls_file, urls_verdict_file)
            verdict = get_verdict(urls_verdict_file)
            print(verdict)
            # os.remove(urls_file)
            # os.remove(urls_verdict_file)
        except Exception as e:
            print("Exception %s in main function" % e)