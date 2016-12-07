
from app_base import AppBase
import sr_feed
import app_config
import urllib.parse
from RssFromFiles import RssFromFiles
import lxml.etree as ET

class RssFilesApp(AppBase):
    """A class that takes a request and returns an RSS feed of the available files."""

    def __init__(self):
        AppBase.__init__(self, 'RssFiles')
        
    def application(self):
        self.trace(4, 'Starting RssFilesApp')

        try:
            u = urllib.parse.urlsplit(self.base_url)
            url = urllib.parse.urlunsplit((u[0], u[1], app_config.rss_files_webpath, u[3], u[4]))
            self.log(5, 'Will look at extensions ', app_config.rss_files_ext, ' in directorys ',  app_config.rss_files_paths, '\nweb is at ' + url)


            rss_gen = RssFromFiles(url, app_config.rss_files_paths, app_config.rss_files_ext)
            feed = rss_gen.get_rss()
            self.log(7, 'Got RSS\n',  ET.tostring(feed, pretty_print=True))            
            feed_data = ET.tostring(feed, encoding='utf8')
            return self.make_response(200, feed_data, 'application/rss+xml')
        except Exception as ex:
            self.log(1, ex)
            raise

     
