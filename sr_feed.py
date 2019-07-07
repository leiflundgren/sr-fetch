#!/usr/bin/python3

import sys
import os
import subprocess
import unittest
import re
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import argparse
import datetime

import sr_helpers
import email.utils

#import xml.etree.ElementTree 
import lxml.etree as ET
import lxml.html as EHTML

import common
from common import is_none_or_empty

from XmlHandler import get_namespace

import Atom2RSS
from sr_prog_page import SrProgramPageParser
from Page2RSS import Page2RSS

ns_atom = 'http://www.w3.org/2005/Atom'
ns_xml = 'http://www.w3.org/XML/1998/namespace'
ns_itunes = "http://www.itunes.com/dtds/podcast-1.0.dtd" 
ns = { 'atom':ns_atom, 'xml': ns_xml, 'itunes':ns_itunes }


class SrFeed(object):
    
    def __init__(self, base_url, feed_url, progid, tracelevel, format, do_proxy, only_episode_with_attachments, program_prefix):
        assert isinstance(base_url, str), 'base_url'
        assert isinstance(feed_url, str), 'feed_url'
        assert isinstance(progid, int) or isinstance(progid, str), 'prog_id'
        assert isinstance(tracelevel, int), 'tracelevel'
        assert isinstance(program_prefix, str), 'program_prefix'

        self.tracelevel = tracelevel
        self.base_url = base_url
        self.feed_url = feed_url
        self.progid = str(progid)
        self.format = format
        self.do_proxy = do_proxy
        self.only_episode_with_attachments = only_episode_with_attachments
        self.program_prefix = program_prefix
        self.content_type = ''
        self.trace(7, 'initaialed a feed reader for ' + feed_url)
        self.trace(9, 'lxml version is ', ET.LXML_VERSION)

    def trace(self, level, *args):
        common.trace(level, 'SrFeed: ', args)

    def build_episode_url(self, avsnitt='', artikel=''):
        
        if avsnitt:
            a_or_a = 'avsnitt=' + avsnitt
        elif artikel:
            a_or_a = 'artikel=' + artikel
        else:
            raise ValueError('must specify either "avsnitt" or "artikel"')

        url = "{url}?programid={programid}&{a_or_a}&tracelevel={tracelevel}&proxy_data={proxy_data}".format(
            url = common.combine_http_path(self.base_url, 'episode'),
            programid = self.progid,
            a_or_a = a_or_a,
            tracelevel = str(self.tracelevel),
            proxy_data = str(self.do_proxy)
            )
        return url 
    
    def get_feed(self):
        (format, feed_et) = self.handle_feed_url(self.feed_url)

        conv_et = self.translate_format(format, feed_et)
        xmlstr = ET.tostring(conv_et, xml_declaration=True, encoding='utf-8', method='xml').decode('utf-8').lstrip()
        if format == 'rss':
            self.content_type = 'application/rss+xml'
        if self.content_type.find('charset') < 0:
            self.content_type = self.content_type + '; charset=' + self.charset
        # ElementTree thinks it has to explicitly state namespace on all nodes. Some readers might have problem with that.
        # This is a hack to remove the namespace
        self.trace(9, 'feed aquired. content-type="' + self.content_type + "\" len=" + str(len(xmlstr)) + " type=" + str(type(xmlstr)))
        xmlstr = xmlstr.replace('<ns0:', '<').replace('</ns0:', '</').replace('xmlns:ns0="','xmlns="') 
        self.trace(9, 'feed aquired. content-type="' + self.content_type + "\" len=" + str(len(xmlstr)) + " \r\n" + xmlstr)
        
        return xmlstr + "\r\n\r\n"
    
    def translate_format(self, format, feed_et):
        if self.format is None:
            self.trace(7, 'format of feed not specified, so ' + self.content_type + ' no altered.')
            return feed_et
        if format == 'rss' and feed_et.tag == 'rss':
            self.content_type = 'application/rss+xml'
            self.trace(7, 'format of feed is rss, as specified, so ' + self.content_type + ' not altered.')
            return feed_et
        if format.find(self.format) >= 0 and self.content_type.find(format) >= 0:
            self.trace(6, 'Content-type is ' + self.content_type + ' so format ' + self.format + ' seems met.')
            return feed_et

        if format.find('rss') >= 0 and self.format.find('atom') >= 0:
            raise NotImplementedError('Cannot convert from rss to atom')

        if format.find('atom') >= 0 and self.format.find('rss') >= 0:
            self.trace(5, 'Translating atom-feed to rss')
            rss = self.translate_atom_to_rss(feed_et)
            self.content_type = 'application/rss+xml'
            return rss
        
        else:
            raise ValueError('Unknown requested content-type ' + self.content_type)

    def translate_atom_to_rss(self, et):        
        return Atom2RSS.Atom2RssNodePerNode().transform(et)


    def handle_feed_url(self, url, u_thing=None):
        """
            Handles a feed.
            Return tuple (format, feed-xml)
        """
        self.trace(4, 'Handling url ' + url)
        if u_thing == None:
            self.trace(7, 'Fetching content from url')
            u_thing = sr_helpers.urllib_open_feed(url)
        if url != u_thing.geturl():
            self.trace(5, 'Urllib automatically redirected to ' + u_thing.geturl())
            return self.handle_feed_url(u_thing.geturl(), u_thing)

        self.set_contenttype_charset(u_thing)
                
        self.trace(5, 'Retreiving content from ' + url)
        self.parse_data_response(u_thing)
        
        if self.content_type.find('application/atom') >= 0 or self.content_type.find('xml') >= 0:
            return self.parse_atom_feed()
        elif self.content_type.find('application/rss') >= 0:
            return self.parse_rss_feed(None)
        elif self.content_type.find('text/html') >= 0:
            return self.parse_html_feed()
        else:
            raise Exception('Content-type of feed is ' + self.content_type + '. Not handled!')

    def parse_data_response(self, u_thing):
        try:
            if self.content_type=='text/html':
                self.dom = EHTML.parse(u_thing)
            else:
                self.dom = ET.parse(u_thing)

            # self.trace(8, 'dom thing ', type(self.dom), dir(self.dom))
            self.xml = get_root(self.dom)
            self.trace(6, 'Successfully parsed urllib-response directly to xml')
        except Exception as ex:
            self.trace(3, 'Failed to parse urllib directly, caught ' + str(ex))
            raise

        #    u_thing = sr_helpers.urllib_open_feed(url)
        #    self.set_contenttype_charset(u_thing)
        #    self.body = u_thing.read()
        #    if len(self.body) == 0:
        #        raise Exception('Got empty body from url', url, ' Unexpected!')

        #    if not self.charset is None:
        #        self.body = self.body.decode(self.charset)

        #    self.trace(7, "Beginning of body:\n" + self.body[0:200])

        #    self.dom = ET.fromstring(self.body)
        #    self.trace(8, 'dom thing ', type(self.dom), dir(self.dom))
        #    #self.xml = self.dom.getroot()
        #    self.xml = get_root(self.dom)

    def set_contenttype_charset(self, u_thing):
        raw_content_type = u_thing.headers['content-type']
        self.trace(7, 'Got response ' + str(u_thing.getcode()) + ' Content-type: ' + raw_content_type)


        colon = raw_content_type.find(';')
        self.content_type = (raw_content_type if colon < 0 else raw_content_type[0:colon]).strip()        

        if (
            self.content_type.find('application/atom') < 0 
            and self.content_type.find('application/rss') < 0 
            and self.content_type.find('xml') < 0
            and self.content_type.find('html') < 0
           ):
            raise Exception('Content-type of feed is ' + self.content_type + '. Not handled!')

        self.charset = None
        if colon > 0:
            p = raw_content_type.find('charset', colon)
            if p > 0:
                p = raw_content_type.find('=', p)
                if p > 0:
                    p = p+1
                    e = raw_content_type.find(';', p)
                    self.charset = raw_content_type[p:]  if e < 0 else raw_content_type[p:e]
        return (self.content_type, self.charset)


    def parse_atom_feed(self):
        
        self.trace(7, 'xml type ' + str(type(self.xml)))
        

        def getfirst(el, xp):
            r = get(el, xp)
            if len(r) > 0:
                return r[0]
            else:
                return ''

        def get(el, xp):
            try:
                #return el.xpath(xp)
                return el.xpath(xp, namespaces=ns)
            except ET.XPathEvalError as e:
                self.trace(2, 'XPath failed ', xp, e)
                raise


        assert(self.xml.tag.endswith('feed'))

        entries = self.xml.findall('atom:entry', ns)
        self.trace(7, 'Found %d entries in atom feed ' % len(entries))
        for entryEl in entries:
            #: type: entryEl: ET.Element

            url = ''

            link = getfirst(entryEl, "atom:link[@type='text/html']")
            if is_none_or_empty(link):
                link = entryEl.find('atom:link', ns)
                link.attrib['type'] = "text/html"
            url = link.attrib['href']

            self.trace(6, 'url for entry ' + url)
        
            media_url = self.fetch_media_url_for_entry(url)

            if not media_url and self.only_episode_with_attachments:
                self.trace(4, 'entry ' + url + ' had no media related. So ignoring.')
                continue

            tag = get_namespace(entryEl.tag) + 'link'
            media_link_el = ET.SubElement(entryEl, tag, rel="enclosure", href=media_url, type='audio/mp4')
        

        return ('atom', self.dom)

    def parse_rss_feed(self, body):
        raise NotImplementedError()

    def parse_html_feed(self):
        def text_url(x):
            pos = self.feed_url.index('?')
            y = self.feed_url[:pos] + '/' + x + self.feed_url[pos:]            
            self.trace(8, 'text_url(' + x + ') --> ' + y)
            return y

        def media_url(x):
            # returns http://leifdev.leiflundgren.com:8091/py-cgi/sr_redirect/6215532.m4a?programid=2480;avsnitt=6215532;tracelevel=9;proxy_data=False
            y = self.build_episode_url(x)
            self.trace(8, 'media_url(' + x + ') --> ' + y)
            return y

        page_parser = SrProgramPageParser(self.tracelevel, self.dom, self.program_prefix)
        episodes = page_parser.episodes()

        self.trace(7, 'Got ' + str(len(episodes)) + ' from html-page\r\n', episodes)

        rss_gen = Page2RSS(text_url, media_url)
        timestamp = page_parser.timestamp
        
        if timestamp is None:
            pass
        elif isinstance(timestamp, datetime.datetime):
            timestamp = email.utils.format_datetime(timestamp)
            #timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(timestamp, datetime.date):
            #timestamp = timestamp.strftime("%Y-%m-%d")
            timestamp = email.utils.format_datetime(timestamp)
        elif isinstance(timestamp, str):
            timestamp = common.parse_datetime_to_rfc822(timestamp)
        else:
            self.trace(6, 'timestamp class-type unhandled: ', timestamp, type(timestamp))
        
        return ('rss', rss_gen.transform(episodes, title=page_parser.title, timestamp=timestamp, description=page_parser.description, logo_url=page_parser.logo, lang=page_parser.lang))



    def fetch_media_url_for_entry(self, url, old_urls=[]):
        orginal_url = url

        if url in old_urls:
            self.trace(1,'Found infinite recursion. Attempting to find url already looked at: ' + url + "\r\n----\r\n" + "\r\n".join(old_urls))
            raise Exception("Found infinite recursion. Attempting to find url already looked.")

        qmark = url.find('?')
        if qmark < 0:
            self.trace(1, 'Url ' + url + ' missing querystring!')
            raise ValueError('Url ' + url + ' missing querystring!')
        qs = urllib.parse.parse_qs(url[qmark+1:])

        programid = qs['programid'][0] if 'programid' in qs else ''
        avsnitt = qs['avsnitt'][0] if 'avsnitt' in qs else ''
        artikel = qs['artikel'][0] if 'artikel' in qs else ''

        # http://sverigesradio.se/sida/artikel.aspx?programid=4427&artikel=6143755
        if avsnitt or artikel:
            url = self.build_episode_url(avsnitt, artikel)
            self.trace(7, 'created sr_redirect url: ' + url)
            return url

        self.trace(8, 'Processing fetching ' + url)
        u_thing = urllib.request.urlopen(urllib.request.Request(url))
        content_type = u_thing.headers['content-type']
        if content_type.find(';') > 0:
            content_type = content_type[0:content_type.find(';')].strip()
        if content_type.find('text/html') < 0:
            self.trace(2, 'Content-type is "' + content_type + '". That was not expected!')

        if u_thing.geturl() != url:
            url = u_thing.geturl()
            self.trace(5, 'seems like redirect to ' + url)
            qs = urllib.parse.parse_qs(url[qmark+1:])
            if 'avsnitt' in qs and 'programid' in qs:
                return self.fetch_media_url_for_entry(url, old_urls.append(orginal_url))
            if 'artikel' in qs and 'programid' in qs:
                self.trace(5, 'Redirected to another artikel. Re-trying that')
                return self.fetch_media_url_for_entry(url, old_urls.append(orginal_url))

        

        raise Exception("Method should have retuned value. Something went wrong...")

        
 

      
    

    def source_is_http(self, x):
        return x.startswith('http')


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

#args 4430 12 
if __name__ == '__main__':
    print(sys.argv)

    do_proxy = False

    for a in sys.argv:
        if a.find('unittest') >= 0:
            common.trace(4, 'Running sr_feed-unitttests')
            sys.exit(unittest.main(argv=['v']))


    parser = argparse.ArgumentParser(description='My favorite argparser.')
    parser.add_argument('-l', '--tracelevel', help='Verbosity level 1 is important like error, 9 is unneeded debuginfo', default=4, type=int)
    parser.add_argument('--avsnitt', help='avsnitt', default=None, type=int, required=False)
    parser.add_argument('--progid', help='progid', default=4430, type=int, required=False)
    parser.add_argument('--artikel', help='artikel', default=None, type=int, required=False)
    parser.add_argument('--feed', help='Full feed url', default=None, required=False)
    parser.add_argument('--url', help='Full feed url', default=None, required=False)
    parser.add_argument('--source', help="Should parse rss or html. rss/html", default='rss', required=False)
    parser.add_argument('--format', help="rss/atom", default='rss', required=False)
    parser.add_argument('--proxy', help="if urls should to proxy data", default=False, required=False)

    r = parser.parse_args(None)


    common.tracelevel = r.tracelevel

    
    if r.feed:
        feed_url = r.feed
    elif r.source=='html' and r.progid:
        feed_url = 'http://sverigesradio.se/sida/avsnitt?programid=' + str(r.progid)
    elif r.url:
        feed_url = r.url
    elif r.progid:
        feed_url = 'http://api.sr.se/api/rss/program/' + str(r.progid)
    else:
        common.trace(1, 'feed/progid required')
        sys.exit(1)

    feeder = SrFeed('http://leifdev.leiflundgren.com:8091/py-cgi/', feed_url, r.progid, common.tracelevel, r.format, r.proxy, False)


    feed = feeder.get_feed()
    
    common.trace(2, common.pretty(feed))
             
      
