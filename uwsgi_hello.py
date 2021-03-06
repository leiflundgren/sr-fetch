import cgi
from app_base import AppBase

class UwsgiHello(AppBase):
    """A sample hello world testbed"""
    def __init__(self, environ, start_response):
        AppBase.__init__(self, 'UwsgiHello', environ, start_response)
        
    def application(self):
        self.start_response("200 OK", [("Content-Type", "text/html")])
        message = self.qs_get('message', 'unknown')[0]
        self.log(3, 'raw message:' + str(message))
        return [("hello there. You said &quot;" + cgi.escape(message) + "&quot;").encode()]

