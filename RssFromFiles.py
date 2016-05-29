#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-

import lxml.etree as ET
import common
import os
import eyed3
import sys
import datetime
import operator

class RssFromFiles(object):
    """description of class"""

    extensions_tuple = ('.mp3')

    def __init__(self, base_url, dir):
        self.script_directory = os.path.dirname(sys.argv[0])
        self.base_url = base_url
        files = self.getAllFiles(dir)
        self.fileInfos = [self.getFileInfo(f[0], f[1]) for f in files]
        self.buildRss()
        pass

    def trace(self, lvl, *args):
        common.trace(lvl, 'RssFromFiles: ', args)

    def getAllFiles(self, dir):
        self.trace(6, 'Looking in dir ' + dir + ' for ', RssFromFiles.extensions_tuple)
        res = []

        if dir[-1] != os.sep: dir += os.sep 
        for root, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                if filename.lower().endswith(RssFromFiles.extensions_tuple):
                    full_filename = os.path.join(root, filename)
                    rel_filename = full_filename[len(dir):]
                    res.append((dir, rel_filename))

        self.trace(8, 'Got files: ', res)
        return res

    def getFileInfo(self, base_dir, rel_file):
        filename = os.path.join(base_dir, rel_file)
        fi = self.read_metadata(filename)
        fi['base_dir'] = base_dir
        fi['rel_file'] = rel_file
        self.trace(7, 'Metadata of ' + filename, fi)
        return fi
       

    def read_metadata(self, filename):
        self.trace(6, 'Reading metadata from ' + filename)
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

    def buildRss(self):
        
        ignored_index, latest_fileinfo = max(enumerate(self.fileInfos), key=operator.itemgetter(0))
        pubDate = common.format_datetime(latest_fileinfo['date'])

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

        for fi in self.fileInfos:
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
            self.trace(7, 'rss enclosure ', ET.tostring(enclosure_link, pretty_print=True))

            ET.SubElement(rss_item, 'link').text = media_url


        self.rss_ = rss_root
        return rss_root

    @property
    def rss(self):
        return self.rss_

if __name__ == '__main__':
    common.tracelevel = 9
    rss =  RssFromFiles('http://leifdev.leiflundgren.com:8891/py-cgi/', 'C:\\Users\llundgren\Downloads').rss
    print(ET.tostring(rss, pretty_print=True))

