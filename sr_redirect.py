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
        if not avsnitt or not programid:
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameters avsnitt and programid is required!']

        self.log(4, 'Attempt to find prog=' + str(programid) + ' and avsnitt=' + str(avsnitt))
        url_finder=SrUrlFinder(programid, avsnitt)

        m4a_url =  url_finder.find()
        self.log(5, 'Result ', m4a_url, ' ', type(m4a_url))
        self.start_response("301 moved permanently", [("Location", m4a_url)])
        #return [cgi.escape(m4a_url)]
        return []

