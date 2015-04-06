import cgi

class AppBase(object):
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

        self.log = environ['wsgi.errors']
        self.qs = cgi.parse_qs(environ['QUERY_STRING'])
    

    def log(self, s):
        print >> self.log, s

    def application(self):
        log('Not implemented. Should be overriden in subclass')
        start_response("501 not implemented", [("Content-Type", "text/html")])
        return ["Not implemented. Should be overriden in subclass"] 



