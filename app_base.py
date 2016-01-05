import cgi
import common

class AppBase(object):
    """Base class for my python web stuff"""
    def __init__(self, app_name, environ, start_response):
        self.app_name = app_name
        self.environ = environ
        self.start_response = start_response

        self.log_handle = environ['wsgi.errors']
        self.qs = cgi.parse_qs(environ['QUERY_STRING'])        

        try:
            common.log_handle = self.log_handle
        except Exception as ex:
            self.log(1, 'while looking at logging, fail, fail, fail: ' + str(ex))
        try:
            common.tracelevel = int(self.qs_get('tracelevel'))
        except Exception as ex:
            pass
        self.tracelevel = common.tracelevel
        self.remote_addr =  environ.get('REMOTE_ADDR')
        self.log(4, 'tracelevel is ' + str(common.tracelevel) + " request from " + self.remote_addr)

        try:
            req = environ['REQUEST_URI']
            s2 = req.find('/',1)
            req = req[0:s2+1]
            self.base_url = environ['UWSGI_SCHEME'] + '://' + environ['HTTP_HOST'] + req
            self.trace(6, 'base_url = ' + self.base_url)
        except Exception as ex:
            self.trace(3, 'Failed to extract base_url ', ex)

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


