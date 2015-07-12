import cgi
from app_base import AppBase
import sr_feed

class SrFeedApp(AppBase):
    """A class that takes a request un query-string, finds the appropriate SR episode and redirects to the download URL"""
    def __init__(self, environ, start_response):
        AppBase.__init__(self, 'SrFeed', environ, start_response)
        
    def application(self):

        programid = self.qs_get('programid') 
        if not programid:
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameter programid is required!']
        if not programid.isdigit():
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['parameter programid must be numbers!']

        proxy_data = self.qs_get('proxy_data', 'False').lower() == 'true'
        format = self.qs_get('format') 

        self.log(4, 'Attempt to find prog=' + str(programid)  + ', proxy_data = ' + str(proxy_data))
        feeder = sr_feed.SrFeed('http://api.sr.se/api/rss/program/' + str(programid), self.tracelevel, format, proxy_data)
        feed_data = feeder.get_feed()
        #self.log(5, 'Result ', m4a_url, ' ', type(m4a_url))
     
        headers = [
            ("Content-Type", feeder.content_type),
            ("Content-Length", str(len(feed_data)))
        ]
        self.start_response("200 OK", headers)
        return [feed_data]


     
