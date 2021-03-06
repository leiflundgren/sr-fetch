﻿#!/usr/bin/python3
# -*- not-codingx: iso-xxx-8859-1 -*-

import lxml.etree as ET

import os.path
import email.utils

from common import trace
from common import pretty
from common import get_el
from common import is_none_or_empty
from common import format_datetime

from XmlHandler import find_first_child
from XmlHandler import find_child_nodes



import urllib.parse

class Page2RSS(object):
    def __init__(self, text_url_formater, media_url_formater):
        self.media_url_formater = media_url_formater
        self.text_url_formater = text_url_formater
        return super(Page2RSS, self).__init__()

    def transform(self, page_dict_list, title, timestamp, description=None, logo_url=None, lang=None, copyright=None):

        ns = 'http://www.w3.org/2005/Atom'
        ns_xml = 'http://www.w3.org/XML/1998/namespace'
        ns_itunes = 'http://www.itunes.com/dtds/podcast-1.0.dtd'

        nsmap = {None: ns, 'xml': ns_xml, 'itunes': ns_itunes }
        nsxpath = {'a':ns, 'xml': ns_xml, 'itunes': ns_itunes }

        def getfirst(el, xp):
            r = get(el, xp)
            if len(r) > 0:
                return r[0]
            else:
                return ''

        def get(el, xp):
            return el.xpath(xp, namespaces=nsxpath)

        ET.register_namespace('itunes', ns_itunes)
        rss_root = ET.Element('rss', version='2.0')
        rss_channel = ET.SubElement(rss_root, 'channel')

        rss_title = ET.SubElement(rss_channel, 'title')
        rss_title.text = title

        if description:
            ET.SubElement(rss_channel, 'description').text = description

        if timestamp:
            ET.SubElement(rss_channel, 'lastBuildDate').text = timestamp
            ET.SubElement(rss_channel, 'pubDate').text = timestamp

        if logo_url:
            rss_image = ET.SubElement(rss_channel, 'image')
            ET.SubElement(rss_image, 'url').text = logo_url
            ET.SubElement(rss_image, 'title').text = title
            ET.SubElement(rss_image, 'link').text = logo_url

        if not lang is None:
            ET.SubElement(rss_channel, 'language').text = lang
        
        if not copyright is None:
            ET.SubElement(rss_channel, 'copyright').text = copyright

                        
        for episode_dict in page_dict_list:
            rss_item = ET.SubElement(rss_channel, 'item')
            

            #rss
            #<item>
            avsnitt_id = episode_dict['avsnitt']
            guid = ET.SubElement(rss_item, 'guid')
            guid.set('isPermaLink', 'false')
            guid.text= avsnitt_id

            ET.SubElement(rss_item, 'title').text= episode_dict['title']
            timestamp = episode_dict['timestamp']
            ET.SubElement(rss_item, 'pubDate').text= email.utils.format_datetime(timestamp)
            ET.SubElement(rss_item, 'description').text = episode_dict.get('description', '')
            
            href_link = ET.SubElement(rss_item, 'link', type="text/html")
            href_link.text= self.text_url_formater(episode_dict['avsnitt'])
            trace(7, 'text href ', ET.tostring(href_link, pretty_print=True))
            
            if not episode_dict.get('logo') is None:
                # <itunes:image href="https://elroycdn.twit.tv/sites/default/files/styles/twit_slideshow_600x450/public/images/episodes/778511/hero/sn721.png?itok=HdA44F8q"/>
                try:
                    img = ET.SubElement(rss_item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image')
                    img.set('href', episode_dict['logo'])
                except:
                    pass
                img = ET.SubElement(rss_item, 'image')
                img.set('href', episode_dict['logo'])


            try:
                media_url = self.media_url_formater(episode_dict['avsnitt'])
                filename, file_ext = os.path.splitext(os.path.basename(urllib.parse.urlparse(media_url).path))
                if file_ext is None or file_ext == '':
                    file_ext = 'm4a'
                enclosure_link = ET.SubElement(rss_item, 'enclosure', type='audio/'+file_ext.strip('.'), url=media_url)
                trace(7, 'page2rss enclosure ', ET.tostring(enclosure_link, pretty_print=True))

                ET.SubElement(rss_item, 'link').text = media_url

            except AttributeError as e:
                trace(1, 'atom_enclosure="', atom_enclosure, '"')
                raise

            

        return rss_root

if __name__ == '__main__':
    dom = ET.parse('sample.atom.xml')
    rss = Page2RSSNodePerNode().transform(dom)
    print(ET.tostring(rss, pretty_print=True))
    pass