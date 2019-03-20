import requests
import urllib2
import db

requests.packages.urllib3.disable_warnings()


def get_url():
    """
    Request a new url from remote server
    :return: a unique url every time
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
                input_url = req.json()['url']
                new_url = db.check_if_url_processed(input_url)
                if new_url:
                    input_url = input_url.strip(' ')
                    if not input_url.endswith('/'):
                        input_url += '/'

                    if not input_url:
                        return get_url()

                    return input_url
                else:
                    return get_url()
        except Exception as e:
            try:
                if e.code:
                    if e.code in [403, 503, 404, 104]:
                        return req.json()['url']
            except:
                with open('lib/phishData/phishing_urls.txt', 'a') as f_writer:
                    f_writer.write(req.json()['url'])
                    f_writer.write("\n")
                return get_url()
        except:
            get_url()
    else:
        get_url()


# if __name__ == '__main__':
#
#     while 1:
#         url = get_url()
#         print(url)
