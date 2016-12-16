

from app_base import AppBase
import sr_feed
import app_config
import urllib.parse
from RssFromFiles import RssFromFiles
import lxml.etree as ET
import os
from flask import Flask, request, send_from_directory
import sys
import codecs 
import glob

class RssFileDownloadApp(AppBase):
    """A class that takes a request and returns an RSS feed of the available files."""

    def __init__(self, filepath, dirs):
        AppBase.__init__(self, 'RssFileDownload')
        self.filepath = filepath
        self.dirs = dirs
        
    def application(self):
        self.trace(4, 'Starting ' + self.app_name)
        self.trace(4, 'Download request of ', self.filepath)
        
        def string_to_list(s):
            chars = []
            for c in s:
                chars.append(c + '  ' + str(ord(c)) + "\n")
            return chars

        def homebrew_encoding_fix(s):
            r = ''
            for c in s:
                if ord(c) >= 256:
                    c = '?'
                r += c
            return r


        try:
            if '..' in self.filepath:
                return self.make_response(400, 'that is a relative url. Naughty!\r\n' + self.filepath, 'text/plain')
            
            u = urllib.parse.urlsplit(self.base_url)
            url = urllib.parse.urlunsplit((u[0], u[1], app_config.rss_files_webpath, u[3], u[4]))
            self.log(5, 'Will look at extensions ', app_config.rss_files_ext, ' in directorys ',  app_config.rss_files_paths, '\nweb is at ' + url)
            
            r = RssFileDownloadApp.find_file_in_dirs(self.dirs, self.filepath, False)

            # http://dev.local:5000/filedownload/Per%20M%E5hl%20och%20Bo%20Sundblad_R%E4ttss%E4ker%20betygss%E4ttningr_F%F6rel%E4sning%2010%20okt%202015.mp4
            if r is None:
                self.log(5, 'charaters in filepath', string_to_list(self.filepath))
                self.filepath = homebrew_encoding_fix(self.filepath)
                self.log(5, '1st attempt failed, recoded filepath to "' + self.filepath + '"')
                r = RssFileDownloadApp.find_file_in_dirs(self.dirs, self.filepath, True)

            #if found_dir is None:
            #    codec = 'latin1'
            #    self.filepath = self.filepath.decode(codec)
            #    self.log(5, '2nd attempt failed, recoded filepath as ' + str(codec) + ' to "' + self.filepath + '"')
            #    found_dir = RssFileDownloadApp.find_file_in_dirs(self.dirs, self.filepath)

            if r is None:
                return self.make_response(404, 'Can\'t find that one buddy\r\n' + self.filepath, 'text/plain')

            (found_dir, self.filepath) = r
            combimed = os.path.join(found_dir, self.filepath)
            self.log(3, 'Will now serve ' + combimed)
            (path, file) = os.path.split(combimed)
            return send_from_directory( path, file )


        except Exception as ex:
            self.log(1, ex)
            raise

    @staticmethod
    def find_file_in_dirs(dirs: [str], file: str, use_wildcard_matchine: bool) -> (str, str) :
        for d in dirs:
            fullpath = os.path.join(d, file)
            if os.path.exists(fullpath):
                return (d, file)

        # Exact path failed, try wildcard
        if use_wildcard_matchine and ( file.find('*') >= 0 or file.find('?') >= 0 ):
            for d in dirs:
                fullpath = os.path.join(d, file)
                for filename in glob.iglob(fullpath):
                    return os.path.split(filename)

        return None
