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
            common.tracelevel = int(self.qs.get('tracelevel'))
        except:
            pass

    def log(self, level, *args):
        # print >> self.log_handle, s
        common.trace(level, args)

    def application(self):
        self.log('Not implemented. Should be overriden in subclass')
        self.start_response("501 not implemented", [("Content-Type", "text/html")])
        return ["Not implemented. Should be overriden in subclass"] 



