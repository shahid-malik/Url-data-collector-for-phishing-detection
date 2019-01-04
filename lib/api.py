import requests
import json


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
        return req.json()['url']
    else:
        get_url()


if __name__ == '__main__':
    url = get_url()
    print(url)
