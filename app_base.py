import cgi
import common

class AppBase(object):
    """Base class for my pythong web stuff"""
    def __init__(self, app_name, environ, start_response):
        self.app_name = app_name
        self.environ = environ
        self.start_response = start_response

        self.log_handle = environ['wsgi.errors']
        self.qs = cgi.parse_qs(environ['QUERY_STRING'])
        try:
            common.log_handle = self.log_handle
        except Exception, ex:
            self.log(1, 'while looking at logging, fail, fail, fail: ' + str(ex))
        try:
            common.tracelevel = int(self.qs_get('tracelevel'))
        except Exception, ex:
            pass
        self.tracelevel = common.tracelevel
        self.remote_addr =  environ.get('REMOTE_ADDR')
        self.log(4, 'tracelevel is ' + str(common.tracelevel) + " request from " + self.remote_addr)

    def log(self, level, *args):
        # print >> self.log_handle, s
        common.trace(level, self.app_name, ': ', args)

    def trace(self, level, *args):
        return self.log(level, args)

    def qs_get(self, keyname, default=None):
        return self.qs.get(keyname, [default])[0]

    def application(self):
        self.log('Not implemented. Should be overriden in subclass')
        self.start_response("501 not implemented", [("Content-Type", "text/html")])
        return ["Not implemented. Should be overriden in subclass"] 

    def qs_get(self, arg):
        return self.qs.get(arg, [None])[0]

