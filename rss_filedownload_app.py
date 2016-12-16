
from app_base import AppBase
import sr_feed
import app_config
import urllib.parse
from RssFromFiles import RssFromFiles
import lxml.etree as ET
import os
from flask import Flask, request, send_from_directory

class RssFileDownloadApp(AppBase):
    """A class that takes a request and returns an RSS feed of the available files."""

    def __init__(self, filepath, dirs):
        AppBase.__init__(self, 'RssFileDownload')
        self.filepath = filepath
        self.dirs = dirs
        
    def application(self):
        self.trace(4, 'Starting ' + self.app_name)
        self.trace(4, 'Download request of ', self.filepath)
        
        try:
            if '..' in self.filepath:
                return self.make_response(400, 'that is a relative url. Naughty!\r\n' + self.filepath, 'text/plain')
            
            u = urllib.parse.urlsplit(self.base_url)
            url = urllib.parse.urlunsplit((u[0], u[1], app_config.rss_files_webpath, u[3], u[4]))
            self.log(5, 'Will look at extensions ', app_config.rss_files_ext, ' in directorys ',  app_config.rss_files_paths, '\nweb is at ' + url)
            
            found_dir = RssFileDownloadApp.find_file_in_dirs(self.dirs, self.filepath)

            if found_dir is None:
                return self.make_response(404, 'Can\'t find that one buddy\r\n', 'text/plain')

            self.log(3, 'Will now serve ' + os.path.join(found_dir, self.filepath))
            return send_from_directory( found_dir, self.filepath )


        except Exception as ex:
            self.log(1, ex)
            raise

    @staticmethod
    def find_file_in_dirs(dirs, file):
        for d in dirs:
            fullpath = os.path.join(d, file)
            if os.path.exists(fullpath):
                return d
        return None



