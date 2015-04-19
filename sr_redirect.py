import cgi
from app_base import AppBase
from sr_url_finder import SrUrlFinder

class SrRedirect(AppBase):
    """A class that takes a request un query-string, finds the appropriate SR episode and redirects to the download URL"""
    def __init__(self, environ, start_response):
        AppBase.__init__(self, environ, start_response)
        
    def application(self):

        avsnitt = self.qs.get('avsnitt', [None])[0]
        programid = self.qs.get('programid', [None])[0] 

        if not avsnitt:
            path = 'string'
            path = environ['PATH_INFO']
            key = 'avsnitt/'
            pos = path.index(key)
            if pos > 0:
                pos += len(key)
                qmark = path.index('?', pos)
                if qmark > 0:
                    avsnitt = path[pos:qmark]
                    self.log(5, 'Extracted avsnitt from query URL ', avsnitt)

        if not avsnitt or not programid:
            self.log(3, 'query-string: ', self.qs)
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameters avsnitt and programid is required!']
        if not avsnitt.isnumeric() or not programid.isnumeric:
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameters avsnitt and programid must be numbers!']

        self.log(4, 'Attempt to find prog=' + str(programid) + ' and avsnitt=' + str(avsnitt))
        url_finder=SrUrlFinder(programid, avsnitt)

        m4a_url =  url_finder.find()
        self.log(5, 'Result ', m4a_url, ' ', type(m4a_url))
        self.start_response("301 moved permanently", [("Location", m4a_url)])
        #return [cgi.escape(m4a_url)]
        return []

     
