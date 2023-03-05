#!/usr/bin/python3

import sys
import glob
import urllib.request, urllib.error, urllib.parse
import unittest
import argparse
import re
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
import json
from xml.dom import minidom 
from xml.dom import minidom 

import common
import sr_helpers

class SrUrlFinder(object):
    
    def __init__(self, progid=None, avsnitt=None, artikel=None):
        if artikel is None and (progid is None or avsnitt is None):
            raise Exception('artikel or progid+avsnitt must be specified')

        self.progid = progid
        self.avsnitt = avsnitt
        self.artikel = artikel

    def trace(self, level, *args):
        common.trace(level, 'SrFinder: ', args)

    def find(self):
        if self.progid and self.avsnitt :
            url = "https://sverigesradio.se/sida/avsnitt/" + str(self.avsnitt) + '?programid=' + str(self.progid)
        elif self.progid:
            url = "http://sverigesradio.se/sida/default.aspx?programid=" + str(self.progid)
        else:
            url = 'https://sverigesradio.se/sida/artikel.aspx?artikel=' + str(self.artikel)
        self.trace(5, "looking at URL " + url)
        return self.handle_url_check_result(url)
    
    def make_hidef(self, url):
        slow_speed_string = '_a96.m4a'
        high_speed_string = '_a192.m4a'

        pos = url.find(slow_speed_string)
        if pos < 0:
            return url

        return url[:pos] + high_speed_string + url[pos+len(slow_speed_string):]
    
    def looks_like_m3u(self, url):
        return url.endswith('.m3u')
 
    def looks_like_mp3(self, url):
        return url.endswith('.mp3')

    def looks_like_m4a(self, url):
        return url.endswith('.m4a')

    def looks_like_sr_program_page(self, url):
        res = not re.match(r'^https?://sverigesradio.se/sida/[\.\w]+/*\?programid=\d+', url) is None
        self.trace(9, 'looks_like_sr_program_page(' + url + ') -->', res)
        # https://sverigesradio.se/sida/avsnitt?programid=4490
        # https://sverigesradio.se/sida/default.aspx?programid=4432
        return res

    def looks_like_sr_episode(self, url):
        # https://sverigesradio.se/sida/avsnitt/412431?programid=4490
        return not re.match(r'^https?://sverigesradio.se/sida/avsnitt/[^=&]+\?programid=\d+', url) is None

    def looks_like_sr_artikel(self, url):
        # sverigesradio.se/sida/artikel.aspx?programid=4427&artikel=6143755
        return not re.match(r'^https?://sverigesradio.se/sida/artikel.asp.*artikel=[=&]+', url) is None

    def looks_like_sr_laddaner(self, url):
        # https://sverigesradio.se/topsy/ljudfil/5032268
        return not re.match(r'https?://sverigesradio.se/topsy/ljudfil/\d+', url) is None

    def looks_like_sr_lyssnaigen(self, url):
        # http://lyssnaigen.sr.se/Isidor/EREG/musikradion_sthlm/2014/08/10_lexsommar_20140806_1700_21e9c23_a96.m4a
        return not re.match(r'https?://lyssnaigen\.sr\.se(/.*)(/.*)(/.*)\.m4a$', url) is None        

    # Sometimes the URL is to a html-page
    def looks_like_html_page(self, url):
        return url.find('radio.aspx') > 0 and url.find('metafile=asx') > 0

    def handle_url_check_result(self, url):
        res = self.handle_url(url)
        #if res is None:
        #    raise ValueError(self.trace(1, 'res-type is ', type(res).__name__))
        self.trace(7, 'handle ', url, ' gave ', res)
        return res

    
    def handle_url(self, url):
        self.trace(9, 'handle_url(' + url + ')')
        
        if self.looks_like_sr_episode(url) or self.looks_like_sr_artikel(url):
            return self.handle_sr_episode(url)

        if self.looks_like_sr_program_page(url):
            return self.handle_sr_program_page(url)
            
        if self.looks_like_sr_laddaner(url):
            return self.handle_sr_laddaner(url)

        if self.looks_like_html_page(url):
            return self.handle_html_url(url)

        if self.looks_like_sr_lyssnaigen(url):
            return self.handle_sr_lyssnaigen(url)
            
        if self.looks_like_m3u(url):
            return self.handle_m3u_url(url)
     
        if self.looks_like_mp3(url):
            return self.handle_mp3_url(url)

        if self.looks_like_m4a(url):
            return self.handle_m4a_url(url)
                   
        self.trace(1, 'URL format was not matched! ' + url)
        raise ValueError('URL format was not matched! ' + url + " Cannot handle this!")

    def handle_m3u_url(self, url):
        self.trace(8, 'Processing m3u ' + url)
        u_thing = urllib.request.urlopen(urllib.request.Request(url))
        content_type = u_thing.headers['content-type']
        if content_type.find(';') > 0:
            content_type = content_type[0:content_type.find(';')].strip()
        if content_type != 'audio/x-mpegurl':
            self.trace(2, 'Content-type is "' + content_type + '". That was not expected!')

        body=u_thing.read()
        for s in body.split('\n'):
            if s.startswith('http'):
                res = self.handle_m4a_url( self.make_hidef( s.strip()) )
                if not res is None:
                    return res
        self.trace(1, 'Could not find any http-url in body: \n', body)
        raise ValueError('Could not find any http-url in body')


    def handle_html_url(self, url):
    
        def find_child_nodes(el, node_names):
            if len(node_names) == 0:
                return [el]
            name = node_names[0]
            res = []
            #sub = el.
            for c in el.childNodes:
                #print c
                #print c._get_localName()
                if c._get_localName() == name:
                    res = res + find_child_nodes(c, node_names[1:] )
            return res
            
    
        self.trace(8, 'Processing html ' + url)
        u_thing = urllib.request.urlopen(urllib.request.Request(url))
        content_type = u_thing.headers['content-type']
        if content_type.find(';') > 0:
            content_type = content_type[0:content_type.find(';')].strip()
        if content_type.find('x-ms-asf') < 0:
            self.trace(2, 'Content-type is "' + content_type + '". That was not expected!')

        asx = u_thing.read()
        self.trace(9, 'Raw asx:\r\n' + asx)
        xml = minidom.parseString(asx)
        self.trace(8, 'Retreived asx\r\n' + xml.toxml())
        
        asx_refs = find_child_nodes(xml, ['asx', 'entry', 'ref'])
        self.trace(7, 'Found %d ref-nodes in asx-data' % len(asx_refs))
        for r in asx_refs:
            res = self.handle_url_check_result( r.attributes['href'].value )
            if not res is None:
                return res
        raise self.trace(1, 'Could not find any http-url in asx-body: \n', asx)
        
                
    def handle_m4a_url(self, url):
        self.trace(6, 'Processing m4a url ' + url + " That is the end result of this program. Returning")
        self.trace(8, 'url-type is ', type(url).__name__)
        return url

    def handle_mp3_url(self, url):
        self.trace(6, 'Processing m4a url ' + url + " That is the end result of this program. Returning")
        self.trace(8, 'url-type is ', type(url).__name__)
        return url

    def handle_sr_program_page(self, url):
        """ Handles download of latest episode from
            https://sverigesradio.se/sida/avsnitt?programid=4490
        """
        self.trace(6, 'handle_sr_program_page(' + url + ')' )
        response = urllib.request.urlopen(url)
        html = response.read()
        
        pos = html.find(b'<span>Lyssna</span>')
        if pos < 0:
            raise ValueError('SR program page lacks Lyssna-tag')
        self.trace(9, 'clip ' + str(pos) + ': ' + html[pos:pos+50])
        
        href= html.rfind('href="', 0, pos)
        if pos < 0:
            raise ValueError('SR program page has, Lyssna-tag but href is missing')
        href = href + 6
        self.trace(9, 'href=' + html[href:href+50])
        
        endp = html.find('"', href)
        self.trace(9, 'href=' + str(href) + '  endp=' + str(endp))
        page_url = urllib.parse.unquote(html[href:endp]).replace('&amp;', '&')
        self.trace(8, 'page_url: ' + page_url)
            
        # Create a list of each bit between slashes
        slashparts = url.split('/')
        # Now join back the first three sections 'http:', '' and 'example.com'
        basename = '/'.join(slashparts[:3])
        url = basename + page_url
        self.trace(4, 'Deduced latest episode to be ' + url)
        
        # raise 'abort!!!!'
        
        return self.handle_url_check_result(url)
        
        #self.trace(0, 'we dont actualy do anything with the program page yet. We should find latest episode or something...')
        #exit()
        

    # https://sverigesradio.se/sida/avsnitt/412431?programid=4490
    def handle_sr_episode(self, url):
        self.trace(5, "looking at SR episode " + url)

        # sverigesradio.se/sida/artikel.aspx?programid=4427&artikel=6143755
        if self.looks_like_sr_artikel(url):
            pass # no work needed for artiel
        elif re.match(r'https://sverigesradio.se/sida/avsnitt/[^&=]+\?programid=\d+&playepisode=[^&=]+', url):
            m = re.match(r'.*playepisode=([^&=]+)', url)
            if not m:
                assert("The URL seems to be missing the playepisode-argument: " + url)
            episode = m.group(1)
        else:
            m = re.match(r'https://sverigesradio.se/sida/avsnitt/([^&=]+)\?programid=[^&=]+', url)
            if not m:
                assert("The URL seems to be missing the avsnitt-i: " + url)
                
            episode = m.group(1)
            self.trace(7, 'deduced episodeid to be ' + episode + '  url: ' + url)
            url = url + "&playepisode=" + episode
            
        response = urllib.request.urlopen(url)
        content_type = response.headers['content-type']
        enc = response.headers['content-encoding'] if 'content-encoding' in response.headers else 'utf-8'
        html = response.read().decode(enc)

        # look for <meta name="twitter:player:stream" content="https://sverigesradio.se/topsy/ljudfil/5032268" />
        
        self.trace(7, 'response ' + content_type + ' len=' + str(len(html)))

        stream = sr_helpers.find_html_meta_argument(html, 'twitter:player:stream')

        if not stream:
            if not episode.isdecimal():
                # need to translate episode-name to id
                # source canidates:        
                #<meta property="al:ios:url" content="sesrplay://?json=%7B%22type%22:%22showEpisode%22,%22id%22:1738255%7D" />
                #<meta property="al:android:url" content="sesrplay://play/episode/1738255" />  
                #<link rel="alternate" type="application/json+oembed" href="https://sverigesradio.se/oembed/episode/1738255" title="Mozarts mytomspunna M&#xE4;ssa i c-moll" />
                #  <button class="audio-button"
                #    data-require="modules/play-on-click modules/set-starttime"
                #    data-audio-type="episode"
                #    data-audio-id="1738255"
                #    aria-label="Lyssna p&#xE5; Mozarts mytomspunna M&#xE4;ssa i c-moll"
                #     data-publication-id="1738255">
        
                str_episode = episode
            
                episode = sr_helpers.find_html_meta_argument(html, 'al:android:url')
                if episode:
                    last_slash = episode.rfind('/')
                    if last_slash > 0:
                        episode = episode[last_slash+1:]
                        self.trace(4, 'found that episode ' + str_episode + " had id " + episode)

            stream = self.handle_playerajax_getaudiourl(episode, url)

        if not stream:
            self.trace(2, "Failed to find twitter:player:stream-meta-header and <link rel=canonical href /> !\n" + html[0:2300] + '...')
            return None
        
        if not stream.startswith('http'):
            stream = 'https://sverigesradio.se' + stream
            self.trace(5, 'modified stream url to ' + stream)
            
        return self.handle_url_check_result(stream)

 
            
    def handle_sr_laddaner(self, url):
        """
            Handles an URL of the form https://sverigesradio.se/topsy/ljudfil/5036246
            @type url: str
        """

        assert isinstance(url, str)

        self.trace(5, "looking at SR laddaner " + url)
         

        rsp = urllib.request.urlopen(urllib.request.Request(url))
        redirect_url = rsp.geturl()
        if redirect_url == url:
            redirect_url = rsp.info().getheader('Location')

        if redirect_url == url:
            raise "response "+ str(rsp.status_code) + "\nHad expected a 302 redirect to lyssnaigen.se.se"

        self.trace(6, 'Rediration to ' + redirect_url)
        return self.handle_url_check_result(redirect_url)
        


    def handle_sr_lyssnaigen(self, url):
        """
            Handles an URL of the form http://lyssnaigen.sr.se/Isidor/EREG/musikradion_sthlm/2014/08/10_lexsommar_20140806_1700_21e9c23_a96.m4a
            @type url: str
        """

        assert isinstance(url, str)

        self.trace(5, "looking at SR lyssnaigen " + url)
        key = '_a96.m4a'
        
        if url.endswith(key):
            url = url[:-len(key)] + '_a192.m4a'
            self.trace(7, 'Changed to 192kbit: ' + url)
        return self.handle_m4a_url(url)
        
    def handle_playerajax_getaudiourl(self, episodeid, referer_url):
        ajax_url = 'https://sverigesradio.se/sida/playerajax/getaudiourl?id=' + episodeid + '&type=episode&quality=high&format=iis'
        self.trace(5, 'ajax-call to ', ajax_url)
        req = urllib.request.Request(ajax_url)
        req.add_header('Referer', referer_url)
        req.add_header('Accept', 'application/json')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        response = urllib.request.urlopen(req)
        content_type = response.headers['content-type']

        if not content_type.startswith('application/json'):
            self.trace(1, 'Response-type ', content_type, ' dont know if we can handle that')

        if 'content-encoding' in response.headers:
            enc = response.headers['content-encoding'] 
        elif content_type.find('charset') > 0:
            begin = content_type.find('charset')+8
            enc = content_type[begin:].strip()
            if enc.find(';') > 0:
                enc = enc[0:enc.find(';')].strip()
        else:
            enc = 'utf-8'
        json_string = response.read().decode(enc)
        try:
            json_object = json.loads(json_string)
            audioUrl = json_object['audioUrl']
            self.trace(5, 'ajax-call yielded ', audioUrl)
            return audioUrl
        except Exception as ex:
            self.trace(1, 'Failed to decode json_string\n' + str(ex) + '\n' + json_string)
            raise # give up


    @staticmethod
    def build_latest_url_from_progid(progid):
        # https://sverigesradio.se/api/radio/radio.aspx?type=latestbroadcast&id=83&codingformat=.m4a&metafile=asx
        return 'https://sverigesradio.se/api/radio/radio.aspx?type=latestbroadcast&id=' + progid + '&codingformat=.m4a&metafile=asx'
    


    @staticmethod
    def find_html_endtag(html, tag_name, start_pos):
        p1 = html.find('/>', start_pos)
        p2 = html.find('</'+tag_name, start_pos)
        if p1<0 and p2<0:
            return -1
        if p1 < 0:
            return p2
        if p2 < 0:
            return p1
        else:
            return min(p1,p2)
        
    @staticmethod
    def find_html_attribute(html, attrib_name, start_pos, end_pos = -1): # --> (attrib-value, endpos)
         pos = start_pos
         while True:
            attr_pos = html.find(attrib_name + '=', pos, end_pos)
            if attr_pos < 0 or attr_pos > end_pos:
                return (None, -1)

            q = '"'
            begin = html.find(q, attr_pos)
            if begin < 0:
                q = "'"
                begin = html.find(q, attr_pos)
            if begin < 0:
                raise ValueError("Failed to find link-tag start quote")
            
            begin = begin+1
            end = html.find(q, begin)
            if end < 0:
                raise ValueError("Failed to find link-tag end quote")

            return (html[begin:end], end+1)
        

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
    parser.add_argument('--url', help='url to retreive html from', default=None, type=str, required=False)

    r = parser.parse_args(None)

    common.tracelevel = r.tracelevel


    redirect_url = SrUrlFinder(r.progid, r.avsnitt, r.artikel).find()

    common.trace(3, 'result "', redirect_url, '"')
             
