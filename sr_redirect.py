import cgi
from app_base import AppBase
from sr_url_finder import SrUrlFinder
import urllib.request, urllib.error, urllib.parse

class SrRedirect(AppBase):
    """A class that takes a request un query-string, finds the appropriate SR episode and redirects to the download URL"""
    def __init__(self, environ, start_response):
        AppBase.__init__(self, 'SrRedirect', environ, start_response)
        
    def application(self):

        avsnitt = self.qs_get('avsnitt')
        programid = self.qs_get('programid')
        artikel = self.qs_get('artikel')
        proxy_data = self.qs_get('proxy_data', 'False').lower() == 'true'


        if not avsnitt and not artikel:
            path = 'string'
            path = self.environ['PATH_INFO']
            key = 'avsnitt/'
            pos = path.find(key)
            if pos > 0:
                pos += len(key)
                qmark = path.index('?', pos)
                if qmark > 0:
                    avsnitt = path[pos:qmark]
                    self.log(5, 'Extracted avsnitt from query URL ', avsnitt)


        if (not avsnitt or not programid) and not artikel:
            self.log(3, 'query-string: ', self.qs)
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameters avsnitt and programid or artikel is required!']
        if avsnitt and not avsnitt.isdigit():
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameters avsnitt must be numbers!']
        if programid and not programid.isdigit():
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameters programid must be numbers!']
        if artikel and not artikel.isdigit():
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameters artikel must be numbers!']

        
        self.log(4, 'Attempt to find prog='+ programid + ', avsnitt=' + str(avsnitt) + ' artikel=' + str(artikel) + ', proxy_data=' + str(proxy_data))
        url_finder=SrUrlFinder(programid, avsnitt, artikel)

        try:
            m4a_url =  url_finder.find()
        except urllib.error.HTTPError as e:
            self.log(2, 'Got HTTP error for prog='+ programid + ', avsnitt=' + str(avsnitt) + ' artikel=' + str(artikel) + ', proxy_data=' + str(proxy_data))
            #self.log(2, 'code', e.code, 'msg', e.msg)
            self.log(2, e)
            self.start_response(str(e.code) + ' ' + e.msg, [])
            return []


        self.log(5, 'Result ', m4a_url, ' ', type(m4a_url))
        if m4a_url is None:
            self.start_response("503 Media not available yet", [])
        elif proxy_data is None:
            self.log(4, 'Proxy mode is one, start proxying...')
            self.start_response("501 Not implemented proxying", [])
        else:
            self.start_response("301 moved permanently", [("Location", m4a_url)])
        #return [cgi.escape(m4a_url)]
        return []

     
