import requests
import urllib2
import db
import json
requests.packages.urllib3.disable_warnings()


def get_url():
    """
    Request a new url from remote server
    :return: a unique everytime
    """
    protocol = 'https'
    server_ip = '10.0.8.79'
    api_url = '{}://{}/worker/getjob/'.format(protocol, server_ip)

    post_data = {'uname': 'snx', 'password': 'top4glory'}
    req = requests.post(api_url, post_data, verify=False)
    if req.status_code == 200:
        try:
            code = urllib2.urlopen(req.json()['url']).code
            if code:
                url = req.json()['url']
                new_url = db.check_if_url_processed(url)
                if new_url:
                    return url
                else:
                    return get_url()
        except Exception as e:
            # print("into exception", e)
            return get_url()
    else:
        get_url()


if __name__ == '__main__':

    while(1):
        url = get_url()
        print(url)
