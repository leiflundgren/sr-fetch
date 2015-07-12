import common
import urllib2
import unittest
import sys

class HttpProxyer(object):
    """A class that act as a http proxy"""

    def __init__(self, url):
        self.app_name = "http_proxy"
        self.url = url
        self.url_thingy = None
        self._content_type = None
        self._content_length = -2

    def log(self, level, *args):
        common.trace(level, self.app_name, ': ', args)

    @property
    def content_length(self):
        self.fetch_headers()
        return self._content_length

    @property
    def content_type(self):
        self.fetch_headers()
        return self._content_type

    def fetch_headers(self):
        if not self.url_thingy is None: return

        self.url_thingy = urllib2.urlopen(self.url)
        self._content_type = self.url_thingy.headers['content-type']
        self._content_length = self.url_thingy.headers['content-length']

    def __iter__(self):
        self.fetch_headers()
        return self

    def next(self):
        raise NotImplementedError('buuuu')

    def close(self):
        if self.url_thingy is not None:
            self.url_thingy.close()

class TestHttpProxyer(unittest.TestCase):
    def test_download_localhost(self):
        proxy = HttpProxyer('http://www.spiegel.de')
        self.assertTrue(proxy.content_type.startswith('text/html'))
        self.assertTrue(proxy.content_length > 0)
    pass

if __name__ == '__main__':
    for a in sys.argv:
        if a.find('unittest') >= 0:
            suite = unittest.TestSuite()
            suite.addTest(TestHttpProxyer("test_download_localhost"))
            runner = unittest.TextTestRunner()
            sys.exit(runner.run(suite))
            # sys.exit(unittest.main(defaultTest='TestHttpProxyer'))
