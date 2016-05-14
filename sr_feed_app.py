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
        format = self.qs_get('format', 'rss') 

        source = self.qs_get('source', 'feed')

        if source == 'feed':
            prog_url = 'http://api.sr.se/api/rss/program/' + str(programid)
        elif source == 'html':
            prog_url = 'http://sverigesradio.se/sida/avsnitt?programid=' + str(programid)
        else:
            self.start_response("500", [("Content-Type", "text/plain")])
            return ['unsupported source. Must be feed/html!']

        self.log(4, 'Attempt to find prog=' + str(programid)  + ', proxy_data = ' + str(proxy_data) + ' from ' + prog_url)
        feeder = sr_feed.SrFeed(self.base_url, prog_url, str(programid), self.tracelevel, format, proxy_data)
        feed_data = feeder.get_feed().encode()
        self.log(9, 'feed_data is ' + str(type(feed_data)) + " len=" + str(len(feed_data)))
        headers = [     
            ("Content-Type", feeder.content_type),
            ("Content-Length", str(len(feed_data)))
        ]
        self.log(4, 'Result is ', feed_data, headers)
        self.start_response("200 OK", headers)
        return [feed_data]


     
