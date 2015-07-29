#!/usr/bin/python

import sys
import os
import unittest
import re

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

        for a in self.html.findall('//a[@data-require="modules/play-on-click"]'):
            url = urlparse(a.attrib['href'])
            path_parts = url.path.split('/')
            
            if len(path_parts) < 3 or path_parts[-2] != 'avsnitt':
                continue
                
            avsnitt = path_parts[-1]

            existing = next((e for e in res if e['avsnitt'] == avsnitt), None)
            if not existing is None:
                continue

            res.append({'avsnitt': avsnitt})

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
    common.trace(3, 'SrProgramPage: result "', episodes, '"')
    
