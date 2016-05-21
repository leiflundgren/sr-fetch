import cgi
from app_base import AppBase
import sr_feed
import app_config
import urllib.parse

class RssFilesApp(AppBase):
    """A class that takes a request and returns an RSS feed of the available files."""

    def __init__(self):
        AppBase.__init__(self, 'RssFiles')
        
    def application(self):

        u = urllib.parse.urlsplit(self.base_url)
        url = urllib.parse.urlunsplit((u[0], u[1], app_config.rss_files_webpath, u[3], u[4]))
        self.log(5, 'Will look at directory ' + app_config.rss_files_path + ' and extensions ', app_config.rss_files_ext, '\nweb is at ' + url)


        feed_data =  RssFromFiles(url, app_config.rss_files_path + ' and extensions ', app_config.rss_files_ext).rss
        self.log(7, 'Got RSS\n' +  ET.tostring(feed_data, pretty_print=True))
        headers = [     
            ("Content-Type", 'application/rss+xml'),
            ("Content-Length", str(len(feed_data)))
        ]
        return self.make_response(200, feed_data, 'application/rss+xml')


     
