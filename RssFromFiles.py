#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-

import lxml.etree as ET
import common
import os
import sys
import datetime
import operator
from time import sleep
import re
import app_config

# to look at meta-data, if we can
try:
    import eyed3
    eyed3_loaded = True
except ImportError: 
    eyed3_loaded = False
    pass


class RssFromFiles(object):
    """description of class"""

    def __init__(self, base_url, dirs, extensions = None):
        self.extensions = extensions if extensions else ('.mp3', '.mp4', '.wav')
        self.script_directory = os.path.dirname(sys.argv[0])
        self.dirs = dirs
        self.base_url = base_url
        if self.base_url[-1] != '/':
            self.base_url += '/' 
        pass

    def trace(self, lvl, *args):
        common.trace(lvl, 'RssFromFiles: ', args)

    def get_rss(self):
        fileInfos = self.getAllFiles(self.dirs)
        return self.buildRss(fileInfos)

    def getAllFiles(self, dirs):
        self.trace(6, 'Looking in for ', self.extensions, ' in ', dirs)
        res = []

        for dir in dirs:
            if dir[-1] != os.sep: dir += os.sep 
            for root, dirnames, filenames in os.walk(dir):
                for filename in filenames:
                    if filename.lower().endswith(self.extensions):
                        full_filename = os.path.join(root, filename)
                        rel_filename = full_filename[len(dir):]
                        try:
                            fileinfo = self.getFileInfo(dir, rel_filename)
                            res.append(fileinfo)
                        except Exception as ex:
                            self.trace(3, "Failed to get fileinfo about " + os.path.join(dir, rel_filename) + " ", ex, ' Skipping file')

        if len(res) > 0:
            self.trace(6, 'Got files: ', res)
        else:
            self.trace(6, 'Got NO files ')
        return res

    def getFileInfo(self, base_dir, rel_file):
        
        fi = self.read_metadata(base_dir, rel_file)
        fi['base_dir'] = base_dir
        fi['rel_file'] = rel_file
        self.trace(7, 'Metadata of ' + os.path.join(base_dir, rel_file), fi)
        return fi
       

    def read_metadata(self, base_dir, rel_file):
        filename = os.path.join(base_dir, rel_file)
        self.trace(6, 'Reading metadata from ' + filename)
        if eyed3_loaded:
            return self.read_metadata_eyed3(filename)
        else:
            return self.read_metadata_filepath(base_dir, rel_file)

    def read_metadata_eyed3(self, filename):
        audiofile = eyed3.load(filename)

        self.trace(9, 'Got audiofile', audiofile)
               
        try:
            mtime = os.path.getmtime(filename)
        except OSError:
            mtime = 0
        last_modified_date = datetime.datetime.fromtimestamp(mtime)

        metadata = { 
            'date': last_modified_date,
            'length': audiofile.info.time_secs,
            'artist': audiofile.tag.artist,
            'album': audiofile.tag.album,
            'album_artist': audiofile.tag.album_artist,
            'title': audiofile.tag.title,
        }
        return metadata

    def read_metadata_filepath(self, base_dir, rel_file):
        filename = os.path.join(base_dir, rel_file)
        self.trace(9, 'finding metadata from filename', filename)
        
        artist=''
        album=''
        album_artist=''
        album.isspace()

        (file_base, file_ext) = os.path.splitext(rel_file)
        if len(file_base) > 0:
            parts = re.findall('[^_\-/\\\\]+', file_base) ## need to escape \ first from string-eval, then from re
            parts = [s for s in parts if s or not s.isspace()]
            artist = parts[0]
            if len(parts) > 1: 
                album = parts[1] 
            if len(parts) > 2: 
                album_artist = parts[2] 
                
        try:
            mtime = os.path.getmtime(filename)
        except OSError:
            mtime = 0
        last_modified_date = datetime.datetime.fromtimestamp(mtime)

        metadata = { 
            'date': last_modified_date,
            #'length': audiofile.info.time_secs,
            'artist': artist,
            'album': album,
            'album_artist': album_artist,
            'title': file_base,
        }

        self.trace(9, 'Got metadata ', filename)
        return metadata

    def buildRss(self, fileInfos):
                
        if len(fileInfos) > 0:
            ignored_index, latest_fileinfo = max(enumerate(fileInfos), key=operator.itemgetter(0))
            pubDate = common.format_datetime(latest_fileinfo['date'])
        else:
            pubDate = common.format_datetime(datetime.datetime.now())

        rss_root = ET.Element('rss', version='2.0')
        rss_channel = ET.SubElement(rss_root, 'channel')

        rss_title = ET.SubElement(rss_channel, 'title')
        rss_title.text = 'Leifs meta-channel from files'

        ET.SubElement(rss_channel, 'language').text = 'sve'
        
        ET.SubElement(rss_channel, 'description').text = 'Just files from my server'
                
        ET.SubElement(rss_channel, 'lastBuildDate').text = pubDate
        ET.SubElement(rss_channel, 'pubDate').text = pubDate


        #rss_image = ET.SubElement(rss_channel, 'image')
        #ET.SubElement(rss_image, 'url').text = getfirst(atom_root, 'a:logo/text()')
        #ET.SubElement(rss_image, 'title').text = rss_title.text
        #ET.SubElement(rss_image, 'link').text = getfirst(atom_root, 'a:link/@href')

        for fi in fileInfos:
            rss_item = ET.SubElement(rss_channel, 'item')

            #rss
            #<item>
            ET.SubElement(rss_item, 'title').text= fi['title']
            ET.SubElement(rss_item, 'description').text = fi['title']
            guid = ET.SubElement(rss_item, 'guid')
            guid.set('isPermaLink', 'false')
            guid.text= fi['rel_file']
            ET.SubElement(rss_item, 'pubDate').text= common.format_datetime(fi['date'])
            
            #href_link = ET.SubElement(rss_item, 'link', type="text/html")
            #href_link.text= 'file:///' + fi['filename']
            
          
            media_url = self.base_url + fi['rel_file']
            enclosure_link = ET.SubElement(rss_item, 'enclosure', type='audio/mpeg', url=media_url)
            self.trace(7, 'rss file enclosure ', ET.tostring(enclosure_link, pretty_print=True))

            ET.SubElement(rss_item, 'link').text = media_url


        return rss_root


if __name__ == '__main__':
    common.tracelevel = 9
    print('Starting test-run')
    rss =  RssFromFiles(
        'http://leifdev.leiflundgren.com:8891/py-cgi/',
        app_config.rss_files_paths,
        app_config.rss_files_ext         
    ).rss
    print(ET.tostring(rss, pretty_print=True))
    sleep(5)

