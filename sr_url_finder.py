#!/usr/bin/python

import sys
import os
import glob
import urllib2
import subprocess
import unittest
import argparse
import datetime
import re
import urllib2
import urllib
import errno
from xml.dom import minidom 
from xml.dom import minidom 

import common

class SrUrlFinder:
    
    def __init__(self, progid=None, avsnitt=None, artikel=None):
        if artikel == 0 and (progid == 0 or avsnitt == 0):
            raise Exception('artikel or progid+avsnitt must be specified')

        self.progid = progid
        self.avsnitt = avsnitt
        self.artikel = artikel

    def find(self):
        if self.progid != 0 and self.avsnitt != 0:
            url = "http://sverigesradio.se/sida/avsnitt/" + str(self.avsnitt) + '?programid=' + str(self.progid)
        else:
            url = 'http://sverigesradio.se/sida/artikel.aspx?artikel=' + str(self.artikel)
        self.trace(5, "looking at URL " + url)
        return self.handle_url_check_result(url)

    def trace(self, level, *args):
        return common.trace(level, args)

    
    def make_hidef(self, url):
        slow_speed_string = '_a96.m4a'
        high_speed_string = '_a192.m4a'

        pos = url.find(slow_speed_string)
        if pos < 0:
            return url

        return url[:pos] + high_speed_string + url[pos+len(slow_speed_string):]
    
    def looks_like_m3u(self, url):
        return url.endswith('.m3u')
 
    def looks_like_m4a(self, url):
        return url.endswith('.m4a')

    def looks_like_sr_program_page(self, url):
        res = not re.match('^http://sverigesradio.se/sida/[\.\w]+/*\?programid=\d+', url) is None
        self.trace(9, 'looks_like_sr_program_page(' + url + ') -->', res)
        # http://sverigesradio.se/sida/avsnitt?programid=4490
        # http://sverigesradio.se/sida/default.aspx?programid=4432
        return res

    def looks_like_sr_episode(self, url):
        # http://sverigesradio.se/sida/avsnitt/412431?programid=4490
        return not re.match('^http://sverigesradio.se/sida/avsnitt/\d+', url) is None

    def looks_like_sr_artikel(self, url):
        # sverigesradio.se/sida/artikel.aspx?programid=4427&artikel=6143755
        return not re.match('^http://sverigesradio.se/sida/artikel.asp.*artikel=\d+', url) is None

    def looks_like_sr_laddaner(self, url):
        # http://sverigesradio.se/topsy/ljudfil/5032268
        return not re.match('http://sverigesradio.se/topsy/ljudfil/\d+', url) is None

    def looks_like_sr_lyssnaigen(self, url):
        # http://lyssnaigen.sr.se/Isidor/EREG/musikradion_sthlm/2014/08/10_lexsommar_20140806_1700_21e9c23_a96.m4a
        return not re.match('http://lyssnaigen\.sr\.se(/.*)(/.*)(/.*)\.m4a$', url) is None        

    # Sometimes the URL is to a html-page
    def looks_like_html_page(self, url):
        return url.find('radio.aspx') > 0 and url.find('metafile=asx') > 0

    def handle_url_check_result(self, url):
        res = self.handle_url(url)
        if res is None:
            raise ValueError(self.trace(1, 'res-type is ', type(res).__name__))
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
     
        if self.looks_like_m4a(url):
            return self.handle_m4a_url(url)
                   
        self.trace(1, 'URL format was not matched! ' + url)
        raise ValueError('URL format was not matched! ' + url + " Cannot handle this!")

    def handle_m3u_url(self, url):
        self.trace(8, 'Processing m3u ' + url)
        u_thing = urllib2.urlopen(urllib2.Request(url))
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
        raise self.trace(1, 'Could not find any http-url in body: \n', body)


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
        u_thing = urllib2.urlopen(urllib2.Request(url))
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
        
                
    def handle_m4a_url(self, m4a_url):
        self.trace(6, 'Processing m4a url ' + m4a_url + " That is the end result of this program. Returning")
        self.trace(8, 'url-type is ', type(m4a_url).__name__)
        #raise m4a_url
        return m4a_url

    def handle_sr_program_page(self, url):
        """ Handles download of latest episode from
            http://sverigesradio.se/sida/avsnitt?programid=4490
        """
        self.trace(6, 'handle_sr_program_page(' + url + ')' )
        response = urllib2.urlopen(url)
        html = response.read()
        
        pos = html.find('<span>Lyssna</span>')
        if pos < 0:
            raise 'SR program page lacks Lyssna-tag'
        self.trace(9, 'clip ' + str(pos) + ': ' + html[pos:pos+50])
        
        href= html.rfind('href="', 0, pos)
        if pos < 0:
            raise 'SR program page has, Lyssna-tag but href is missing'
        href = href + 6
        self.trace(9, 'href=' + html[href:href+50])
        
        endp = html.find('"', href)
        self.trace(9, 'href=' + str(href) + '  endp=' + str(endp))
        page_url = urllib.unquote(html[href:endp]).replace('&amp;', '&')
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
        

    # http://sverigesradio.se/sida/avsnitt/412431?programid=4490
    def handle_sr_episode(self, url):
        self.trace(5, "looking at SR episode " + url)

        # sverigesradio.se/sida/artikel.aspx?programid=4427&artikel=6143755
        if self.looks_like_sr_artikel(url):
            pass # no work needed for artiel
        elif not re.match('http://sverigesradio.se/sida/avsnitt/\d+\?programid=\d+&playepisode=\d+', url):
            m = re.match('http://sverigesradio.se/sida/avsnitt/(\d+)\?programid=\d+', url)
            if not m:
                assert("The URL seems to be missing the avsnitt-i: " + url)
                
            url = url.rstrip('&') + '&playepisode=' + m.group(1)
            self.trace(7, 'deduced episodeid to be ' + m.group(1) + '  url: ' + url)
            
            return self.handle_url_check_result(url)

        response = urllib2.urlopen(url)
        html = response.read()

        # look for <meta name="twitter:player:stream" content="http://sverigesradio.se/topsy/ljudfil/5032268" />
        
        stream = self.find_html_meta_argument(html, 'twitter:player:stream')
        
        if not stream:
            raise "Failed to find twitter:player:stream-meta-header!"
        
        if not stream.startswith('http'):
            stream = 'http://sverigesradio.se' + stream
            self.trace(5, 'modified stream url to ' + stream)
            
        return self.handle_url_check_result(stream)

    def filename_from_html_content(self, html):
        self.trace(8, 'Trying to deduce filename from html-content.')
        programname = ''
        displaydate = self.find_html_meta_argument(html, 'displaydate')
        programid = self.find_html_meta_argument(html, 'programid')

        # change date from 20141210 to 2014-12-10            
        displaydate =  displaydate[:-4] + '-' +  displaydate[-4:-2] + '-' + displaydate[-2:]

        title = self.find_html_meta_argument(html, 'og:title')

        idx = title.rfind(' - ')
        if idx < 0:
            self.trace(8, 'programname is not part of og:title, truing twitter:title')
            title = self.find_html_meta_argument(html, 'twitter:title')
            idx = title.rfind(' - ')

        if idx > 0:
            programname = title[idx+3:].strip()
            title = title[:idx]
  
        programname = common.unescape_html(programname)
        programname = programname.replace('/', ' ').rstrip(' .,!')
        if programname == 'Lordagsmorgon i P2':
            programname = 'Lordagsmorgon'
        self.trace(7, 'programname is ' + programname)


        parts = title.split(' ')

        # trim date/time from end
        lastToKeep = 0
        for idx in range(0, len(parts)):
            # self.trace(9, 'idx=' + str(idx) + ': "' + parts[idx] + '"')
            if re.match('\d+(:\d+)*', parts[idx]):
                pass
            elif parts[idx] == 'kl':
                pass
            elif common.is_swe_month(parts[idx]):
                pass
            else:
                self.trace(9, 'idx=' + str(idx) + ' is to keep "' + parts[idx] + '"')                    
                lastToKeep = idx
                continue
            self.trace(9, 'skipping idx=' + str(idx) + ' "' + parts[idx] + '" from title')

        title = ' '.join(parts[0:lastToKeep+1])
        title = common.unescape_html(title)
        title = title.replace('/', ' ').strip(' .,!')

        self.trace(4, 'new title is ' + title)

        filename = programname + ' ' + displaydate + ' ' + title + '.m4a'
        self.trace(4, 'filename: ' + self.filename)
        
        return filename
            
    def handle_sr_laddaner(self, url):
        """
            Handles an URL of the form http://sverigesradio.se/topsy/ljudfil/5036246
            @type url: str
        """

        assert isinstance(url, str)

        self.trace(5, "looking at SR laddaner " + url)
         

        rsp = urllib2.urlopen(urllib2.Request(url))
        redirect_url = rsp.geturl()
        if redirect_url == url:
            redirect_url = rsp.info().getheader('Location')

        if redirect_url == url:
            raise "response "+ str(response.status_code) + "\nHad expected a 302 redirect to lyssnaigen.se.se"

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
        
    @staticmethod
    def build_latest_url_from_progid(progid):
        # http://sverigesradio.se/api/radio/radio.aspx?type=latestbroadcast&id=83&codingformat=.m4a&metafile=asx
        return 'http://sverigesradio.se/api/radio/radio.aspx?type=latestbroadcast&id=' + progid + '&codingformat=.m4a&metafile=asx'


    #wget -nv -O "$1" `wget -O - -q --limit-rate=44k "$2" | grep http | perl -p -e 's/_a96.m4a/_a192.m4a/' | tr -d '\r\n'` &
    def wget_command_line(self, input_m4a_url, output_filename):
        cmd = [ 'wget' ]

        if self.tracelevel <= 3:
            cmd.append('-q')
        elif self.tracelevel <= 7:
            cmd.append('-nv')
        elif self.tracelevel <= 8:
            cmd.append('-v')
        else:
            cmd.append('-d')

        cmd.extend(['-O', output_filename.replace('/', '_')])

        if not self.downloadlimit is None:
            cmd.append('--limit-rate=' + str(self.downloadlimit))
        cmd.append(input_m4a_url)
        return cmd


    def post_process_file(self):
        self.trace(5, 'Processing downloaded file ' + self.filename)

        new_files = None
        try:
            rkn = remove_kulturnytt.RemoveKulturnytt(self.filename, self.overwrite, self.tracelevel, True)
            new_files = rkn.main()
            self.trace(7, 'Kulturnytt removal done, parts: ' + str(new_files))
        except OSError as e:
            if e.errno == errno.ENOENT:
                self.trace(4, 'Failed to launch ffmpeg. Ignoring splitting files.')
            else:
                raise e
        
        if new_files is None:
            new_files = [self.filename] # reset if below succeeds

        for f in new_files:
            self.trace(5, 'Setting metadata of ' + str(f))
            sr_set_metadata.SrSetMetadata(f, self.overwrite, self.tracelevel, None).main()


        self.trace(6, 'Post-processing done')

    def find_html_meta_argument(self, html, argname):
        idx = html.find('<meta name="' + argname + '"')
        if idx < 0:
            idx = html.find('<meta property="' + argname + '"')
        if idx < 0:
            self.trace(6, "Failed to find meta-argument " + argname)
            return None
        
        # self.trace(8, 'found ' + html[idx:idx+200])
        
        idx = html.find('content=', idx)
        if idx < 0:
            self.trace(6, "Failed to find content-tag for meta-argument " + argname)
            return None
        
        begin = html.find('"', idx)
        if begin < 0:
            raise "Failed to find content-tag start quote"
            
        begin = begin+1
        end = html.find('"', begin)
        if end < 0:
            raise "Failed to find content-tag end quote"
            
        val = html[begin:end]
        self.trace(7, "value of "+ argname + " is '" + val + "'")
        return val


    def assertTargetDoesntExistOrOverwrite(self):
        if self.overwrite:
            return
        if self.filename is None:
            return
        (file_no_ext, ext) = os.path.splitext(self.filename)
        existing = glob.glob(file_no_ext + '*.m4a')
        if len(existing) == 0:
            return
            
        self.trace(2, 'Target-file(s) ', existing, ' already exists on disk.')
        sys.exit(0)
        
        

class TestSrFetch(unittest.TestCase):
    pass

if __name__ == '__main__':
    for a in sys.argv:
        if a.find('unittest') >= 0:
            sys.exit(unittest.main())

    parser = argparse.ArgumentParser(description='My favorite argparser.')
    parser.add_argument('-l', '--tracelevel', help='Verbosity level 1 is important like error, 9 is unneeded debuginfo', default=4, type=int)
    parser.add_argument('--avsnitt', help='avsnitt', default=0, type=int, required=False)
    parser.add_argument('--progid', help='progid', default=0, type=int, required=False)
    parser.add_argument('--artikel', help='artikel', default=0, type=int, required=False)

    r = parser.parse_args(None)

    common.tracelevel = r.tracelevel


    redirect_url = SrUrlFinder(r.progid, r.avsnitt, r.artikel).find()
    common.trace(3, 'result "' + redirect_url + '"')
             
