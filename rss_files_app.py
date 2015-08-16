import cgi
from app_base import AppBase
import sr_feed
import app_config
import urlparse

class RssFilesApp(AppBase):
    """A class that takes a request and returns an RSS feed of the available files."""

    def __init__(self, environ, start_response):
        AppBase.__init__(self, 'RssFiles', environ, start_response)
        
    def application(self):

        u = urlparse.urlsplit(self.base_url)
        url = urlparse.urlunsplit((u[0], u[1], app_config.rss_files_webpath, u[3], u[4]))
        self.log(5, 'Will look at directory ' + app_config.rss_files_path + ' and extensions ', app_config.rss_files_ext, '\nweb is at ' + url)


        feed_data =  RssFromFiles(url, app_config.rss_files_path + ' and extensions ', app_config.rss_files_ext).rss
        self.log(7, 'Got RSS\n' +  ET.tostring(feed_data, pretty_print=True))
        headers = [     
            ("Content-Type", 'application/rss+xm'),
            ("Content-Length", str(len(feed_data)))
        ]
        self.start_response("200 OK", headers)
        return [feed_data]


     
