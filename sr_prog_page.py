#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import sys
import os
import unittest
import re
import sr_helpers
import datetime
import XmlHandler

from urlparse import urlparse


import argparse

#import xml.etree.ElementTree 
import lxml.etree as ET
import lxml.html as EHTML

import common
from common import is_none_or_empty

from XmlHandler import get_namespace


class SrProgramPage:

    def __init__(self, program_id, tracelevel):
        self.tracelevel = tracelevel
        self.program_id = str(program_id)

    def trace(self, level, *args):
        common.trace(level, 'SrProgramPage: ', args)

    def get_program_url(self):
        return 'http://sverigesradio.se/sida/avsnitt?programid=' + self.program_id

    def fetch_page(self):
        url = self.get_program_url()
        self.trace(5, 'fetching ' + url)
        self.html = EHTML.parse(url)
        self.trace(9, 'got page \r\n', ET.tostring(self.html, pretty_print=True))
        #print ET.tostring(self.html, pretty_print=True)

    def parse_page(self):

        # good links are 
        # <a href="/sida/avsnitt/587231?programid=2480&amp;playepisode=587231" aria-label="Lyssna(161 min)" class="btn btn-solid play-symbol play-symbol-wide play" data-require="modules/play-on-click">&#13;
        # <a href="/sida/avsnitt/587242?programid=2480" class="btn2 btn2-image btn2-image-foldable" data-require="modules/play-on-click">

        res = []

        # for timestamp_span in self.html.find('span class="page-render-timestamp hidden" data-timestamp="2015-07-28 19:11:25" />&#13;
        html_timestamp = datetime.datetime.today()
        timestamp_span = self.html.find('//span[@class="page-render-timestamp hidden"]')
        if not timestamp_span is None:
            html_timestamp = common.parse_datetime(timestamp_span.attrib['data-timestamp'])


        divs_to_search = self.html.findall('//div[@class="audio-box-content"]') + self.html.findall('//div[@class="audio-episode-content"]')

        def find_a_playonclick(root):
            a_play = XmlHandler.find_element_attribute(root, 'a', 'data-require', "modules/play-on-click")
            return None if a_play is None else a_play.attrib['href'] 

        """ 
            Find Sändes-keyword and extract time from that.
        """
        def find_transmit_time(root):
            for span in XmlHandler.findall_element_attribute(root, 'span', 'class', 'date'):
                # Could also have checked text-context
                #if span.text.find('S&#228;ndes') >= 0 or span.text.find(u'S\xe4ndes') >= 0:

                abbr = span.find('abbr[@title]')
                try:
                    return sr_helpers.parse_sr_time_string(abbr.attrib['title'], html_timestamp)
                except ValueError:
                    pass
            return None

        def find_title(root):
            # <div class="audio-box-title">
            try:
                audio_box_title = XmlHandler.find_element_attribute(root, 'div', 'class', "audio-box-title")
                title_span = XmlHandler.find_element_attribute(audio_box_title, 'span', 'class', "responsive-audio-box-title")
                return title_span.text_content().strip()
            except AttributeError:
                pass
            # <div class="audio-episode-title audio-info">
            try:
                audio_episode_title = XmlHandler.find_element_attribute(root, 'div', 'class', "audio-episode-title audio-info")
                title_span = XmlHandler.find_element_attribute(audio_episode_title, 'span', 'class', "header2")
                return title_span.text_content().strip()
            except AttributeError:
                pass
            return None

        for div in divs_to_search:

            a_href = find_a_playonclick(div)
            if a_href is None:
                continue

            url = urlparse(a_href)
            path_parts = url.path.split('/')
            
            if len(path_parts) < 3 or path_parts[-2] != 'avsnitt':
                continue
                
            avsnitt_id = path_parts[-1]

            avsnitt_timestamp = find_transmit_time(div)

            avsnitt_title = find_title(div)

            avsnitt = next((e for e in res if e['avsnitt'] == avsnitt_id), None)
            if avsnitt is None:
                avsnitt = {'avsnitt': avsnitt_id }
                res.append(avsnitt)

            if not avsnitt_timestamp is None:
                avsnitt['timestamp'] = avsnitt_timestamp

            if not avsnitt_title is None:
                avsnitt['title'] = avsnitt_title


        return res

    def find_episodes(self):
        self.fetch_page()
        return self.parse_page()
        


def get_root(element_thing):
    # lxml.etree._ElementTree :: getroot
    if isinstance(element_thing, ET._ElementTree):
        return element_thing.getroot()
    # <type 'lxml.etree._Element'> :: getroottree
    if isinstance(element_thing, ET._Element):
        return get_root(element_thing.getroottree())
            
    return element_thing

class TestSrFetch(unittest.TestCase):
    pass


if __name__ == '__main__':
    for a in sys.argv:
        if a.find('unittest') >= 0:
            sys.exit(unittest.main())

    parser = argparse.ArgumentParser(description='My favorite argparser.')
    parser.add_argument('-l', '--tracelevel', help='Verbosity level 1 is important like error, 9 is unneeded debuginfo', default=4, type=int)
    parser.add_argument('--avsnitt', help='avsnitt', default=None, type=int, required=False)
    parser.add_argument('--progid', help='progid', default=None, type=int, required=False)
    parser.add_argument('--artikel', help='artikel', default=None, type=int, required=False)

    r = parser.parse_args(None)

    common.tracelevel = r.tracelevel
    
    episodes = SrProgramPage(r.progid, common.tracelevel).find_episodes()
    common.trace(3, 'SrProgramPage: result: ' , sorted(episodes, key=lambda ep: ep['avsnitt']))
    
