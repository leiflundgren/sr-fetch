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
        artikel = self.qs.get('artikel', [None])[0]
        if not avsnitt and not artikel :
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

        self.log(4, 'Attempt to find prog="' + str(programid) + '", avsnitt="' + str(avsnitt) + '" and artikel="' + artikel + '"')
        url_finder=SrUrlFinder(programid, avsnitt, artikel)

        m4a_url =  url_finder.find()
        self.log(5, 'Result ', m4a_url, ' ', type(m4a_url))
        self.start_response("301 moved permanently", [("Location", m4a_url)])
        #return [cgi.escape(m4a_url)]
        return []

     
