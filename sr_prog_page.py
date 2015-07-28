#!/usr/bin/python

import sys
import os
import unittest
import re
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
        self.program_id = program_id

    def trace(self, level, *args):
        common.trace(level, 'SrProgramPage: ', args)

    def get_program_url(self):
        return 'http://sverigesradio.se/sida/avsnitt?programid=' + self.program_id

    def fetch_page(self):
        self.html = EHTML.parse(self.get_program_url())

    def parse_page(self):
        pass

    def find_episodes(self):
        pass


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
    
