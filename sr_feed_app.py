import cgi
from app_base import AppBase
import sr_feed

class SrFeedApp(AppBase):
    """A class that takes a request un query-string, finds the appropriate SR episode and redirects to the download URL"""
    def __init__(self, environ, start_response):
        AppBase.__init__(self, environ, start_response)
        
    def application(self):

        programid = self.qs.get('programid', [None])[0] 
        if not programid:
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameter programid is required!']
        if not programid.isnumeric:
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameter programid must be numbers!']

        self.log(4, 'Attempt to find prog=' + str(programid))
        feed = sr_feed.SrFeed('http://api.sr.se/api/rss/program/' + str(programid), self.tracelevel)
        #self.log(5, 'Result ', m4a_url, ' ', type(m4a_url))
     
        self.start_response("200 OK", [("Content-Type", feed.content_type)])
        return [feed]


     