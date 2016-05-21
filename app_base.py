import cgi
import common
import sys
import flask

class AppBase(object):
    """Base class for my python web stuff"""
    def __init__(self, app_name):
        self.app_name = app_name
#        self.environ = environ
#        self.start_response = start_response


 #       self.log_handle = environ['wsgi.errors']
        self.log_handle = sys.stdout
#        self.qs = cgi.parse_qs(environ['QUERY_STRING'])        

        
        try:
            common.log_handle = self.log_handle
        except Exception as ex:
            raise Exception(1, 'while looking at logging, fail, fail, fail: ' + str(ex), ex)
        try:
            common.tracelevel = int(self.qs_get('tracelevel', 3))
        except Exception as ex:
            common.tracelevel=3
            self.log(3, 'Failed to get tracelevel from args. Using level 3', ex )
        self.log(7, 'creating ' + app_name +  ' tracelevel=' + str(common.tracelevel))
        self.tracelevel = common.tracelevel
        self.remote_addr =  flask.request.remote_addr
        self.log(4, 'tracelevel is ' + str(common.tracelevel) + " request from " + self.remote_addr)

 #       try:
        req = flask.request.url_root
        self.log(6, 'request.url: ' + req)
   #     p = req.indexof('/',9)
        self.base_url = req
        self.app_url = flask.request.url
        qmark = self.app_url.find('?')
        if qmark > 0:
            self.app_url = self.app_url[:qmark]
        self.trace(6, 'base_url = ' + self.base_url  + '   app_url=' + self.app_url)
  #  except Exception as ex:
  #          self.trace(3, 'Failed to extract base_url ', type(ex), ex)

    def log(self, level, *args):
        common.trace(level, self.app_name, ': ', args)

    def trace(self, level, *args):
        return self.log(level, args)

    def qs_get(self, keyname, default=None):
        try:
            v = flask.request.args.get(keyname)
            return default if v is None else v
        except AttributeError as ex:
            # self.log(3, 'QueryString ' + keyname + ' not set. Returning default ' + str(default) + " ex: ", ex)
            return default
        except Exception as ex:
            self.log(1, 'Failed to get querystring arg:', ex)
            raise
        
        
    def application(self):
        self.log(0, 'Not implemented. Should be overriden in subclass')
        return self.make_response(501, "Not implemented. Should be overriden in subclass", "text/html")

    def make_response(self, statuscode, body, content_type = None, headers = []):
        if statuscode >= 300 and statuscode < 400:
            self.log(5, 'redirecting ', statuscode, ' to ', body)
            return flask.redirect(body, statuscode)
        r = flask.make_response(body)
        if content_type:
            r.headers['Content-Type'] = content_type
        for (h, v) in headers:
            r.headers[h] = v
        return r
     