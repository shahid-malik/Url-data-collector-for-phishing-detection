import os
from os import listdir
from os.path import isfile, join
from BeautifulSoup import BeautifulSoup
import urllib2
from urlparse import urlparse


def get_domain(input_url):
    """
    Get the main domain of the url provided
    :param input_url:
    :return: domain of url(string)
    """
    domain = ''
    try:
        if input_url is not None:
            parsed_uri = urlparse(input_url)
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    except Exception as exp:
        print("Exception in getting domain from given url with exception %s" % exp)
    return domain


def process_request_gsb(url, url_html):
    """
    Get all the outgoing links of the page hit by  given url, provide processed urls with the http or https protocol
    """
    try:
        page = open(url_html)
        soup = BeautifulSoup(page.read())
    except Exception as exp:
        print("coult not process the file: {} with exception {}".format(url_html, exp))
        return


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
                ahref_url = str(url + ahref_url)
            url_list.add(ahref_url)
        except Exception as exp:
            print("exception extracting link from <a> tag", exp)

    for link in links:
        try:
            link_url = str(link['href'])
            if not link_url.startswith('http'):
                link_url = str(url + link_url)
            url_list.add(link_url)
        except Exception as exp:
            print("exception extracting link from <link> tag", exp)

    for iframe in iframes:
        try:
            iframe_url = str(iframe['src'])
            if not iframe_url.startswith('http'):
                iframe_url = str(url + iframe_url)
            url_list.add(iframe_url)
        except Exception as exp:
            print("exception extracting link from <iframe> tag", exp)

    for input in inputs:
        try:
            i_url = str(input['src'])
            if not i_url.startswith('http'):
                i_url = str(url + i_url)
            url_list.add(i_url)
        except:
            print("exception extracting link from <input> tag")

    for img in imgs:
        try:
            img_url = str(img['src'])
            if not img_url.startswith('http'):
                img_url = str(url + img_url)
            url_list.add(img_url)
        except Exception as exp:
            print("exception extracting link from <img>", exp)
    return url_list


def get_all_og_urls(package_dir, type, file_dir):
    """
    Get the outgoing urls from the packages provided. It will be used for the gsb verdict
    :param package_dir:
    :param type:
    :param file_dir:
    :return:
    """
    file_dir = file_dir+'/data/'
    file_name = file_dir+type+'_og.csv'
    total_files = 0
    url_list = []
    for root, dirs, files in os.walk(package_dir):
        for file in files:
            html_file = root.split('/')[-1] + '.html'
            if 'url.txt' in file:
                total_files += 1
                with open(root+'/'+file) as infile:
                    line = infile.readlines()[0]
                    url = line.split(' :')[1].strip('\n')+'\n'
                    url_list.append(url+"\n")
                print("***** Processing {}, {} ******".format(url, root.split('/')[-1]))
                url = url.strip('\n')
                og_urls = process_request_gsb(url, root+'/'+html_file)
                items = map(lambda x:x, og_urls)

                og_urls_new = []
                for item in items:
                    og_urls_new.append(url+','+item+"\n")

                with open(file_name, 'a') as outfile:
                    outfile.writelines(og_urls_new)

    # print("Total urls extracted from {} packages:  {}".format(type, total_files))
    # if not os.path.exists(file_dir):
    #     os.makedirs(file_dir)
    # try:
    #     with open(file_name, 'w') as outfile:
    #         outfile.writelines(url_list)
    # except Exception as exp:
    #     print(exp)


def get_urls_from_package(package_dir, type, file_dir):

    file_dir = file_dir+'/data/'

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file_name = file_dir+type+'.csv'

    total_files = 0
    url_list = []
    for root, dirs, files in os.walk(package_dir):
        for file in files:
            if 'url.txt' in file:
                total_files += 1
                with open(root+'/'+file) as infile:
                    line = infile.readlines()[0]
                    url = line.split(' :')[1].strip('\n')+'\n'
                    url_list.append(url)
    print("Total urls extracted from {} packages:  {}".format(type, total_files))

    write_to_file(file_name, url_list)


def write_to_file(file_name, data_list):
    """
    write to a csv file
    :param file_name:
    :param data_list:
    :return:
    """
    try:
        with open(file_name, 'w') as outfile:
            outfile.writelines(data_list)
    except Exception as exp:
        print(exp)


if __name__ == '__main__':
    benign_package_path = '/home/shahid/Downloads/benign_packages'
    malicious_package_path = '/home/shahid/Downloads/openphish_packages'
    curr_dir = os.path.dirname(os.path.realpath(__file__))

    # get_urls_from_package(benign_package_path, 'benign', curr_dir)
    # get_urls_from_package(malicious_package_path, 'malicious', curr_dir)

    get_all_og_urls(malicious_package_path, 'malicious', curr_dir)
    get_all_og_urls(benign_package_path, 'benign', curr_dir)
