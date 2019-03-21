import hashlib


class UrlPreProcessing:
    def __init__(self, url):
        self.url = url

    def get_url_md5(self):
        """ generate md5 hash of the url """
        try:
            m = hashlib.md5()
            m.update(self.url)
            md5_hash = m.hexdigest()
        except:
            md5_hash = ''
        return md5_hash