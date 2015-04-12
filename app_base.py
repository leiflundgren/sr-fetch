import cgi
import common

class AppBase(object):
    """Base class for my pythong web stuff"""
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

        self.log_handle = environ['wsgi.errors']
        self.qs = cgi.parse_qs(environ['QUERY_STRING'])
        try:
            common.log_handle = self.log_handle
        except Exception, ex:
            self.log(1, 'while looking at logging, fail, fail, fail: ' + str(ex))
        try:
            common.tracelevel = int(self.qs.get('tracelevel', [None])[0])
        except Exception, ex:
            pass
        self.log(4, 'tracelevel is ' + str(common.tracelevel))

    def log(self, level, *args):
        # print >> self.log_handle, s
        common.trace(level, args)

    def application(self):
        self.log('Not implemented. Should be overriden in subclass')
        self.start_response("501 not implemented", [("Content-Type", "text/html")])
        return ["Not implemented. Should be overriden in subclass"] 



