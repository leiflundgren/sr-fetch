#!/usr/bin/python

import sys
import os
import subprocess
import unittest
import re
import urllib2
import urllib

from xml.etree import ElementTree as ET

import common

ns = {'atom': "http://www.w3.org/2005/Atom"}

class SrFeed:
    
    def __init__(self, feed_url, tracelevel):
        self.tracelevel = tracelevel
        self.feed_url = feed_url
        self.trace(7, 'init looking at ' + feed_url)

    def trace(self, level, *args):
        common.trace(level, args)

    def get_feed(self):
        et = self.handle_feed_url(self.feed_url)
        xmlstr = ET.tostring(et, encoding='utf-8', method='xml')
        if self.content_type.find('charset') < 0:
            self.content_type = self.content_type + '; charset=utf-8'
        # ElementTree thinks it has to explicitly state namespace on all nodes. Some readers might have problem with that.
        # This is a hack to remove the namespace
        xmlstr = xmlstr.replace('<ns0:', '<').replace('</ns0:', '</').replace('xmlns:ns0="','xmlns="')
        return xmlstr
    

    def handle_feed_url(self, url, u_thing=None):
        self.trace(4, 'Handling url ' + url)
        if u_thing == None:
            self.trace(7, 'Fetching content from url')
            u_thing = urllib2.urlopen(urllib2.Request(url))
        if url != u_thing.geturl():
            self.trace(5, 'Urllib automatically redirected to ' + u_thing.geturl())
            return self.handle_url(self, u_thing.geturl(), u_thing)

        raw_content_type = u_thing.headers['content-type']
        self.trace(7, 'Got response ' + str(u_thing.getcode()) + ' Content-type: ' + raw_content_type)


        colon = raw_content_type.find(';')
        self.content_type = raw_content_type[0:colon].strip()        
        if self.content_type.find('application/atom') < 0 and self.content_type.find('application/rss') < 0:
            raise Exception('Content-type of feed is ' + content_type + '. Not handled!')

        self.trace(5, 'Retreiving content from ' + url)
        self.body = u_thing.read()
        if len(self.body) == 0:
            raise Exception('Got empty body from url Unexpected!')

        charset = None
        if colon > 0:
            p = raw_content_type.find('charset', colon)
            if p > 0:
                p = raw_content_type.find('=', p)
                if p > 0:
                    p = p+1
                    e = raw_content_type.find(';', p)
                    charset = raw_content_type[p:]  if e < 0 else raw_content_type[p:e]
                
        if not charset is None:
            self.body = self.body.decode(charset)

        self.trace(7, "Beginning of body:\n" + self.body[0:100])

        #self.xml = XmlHandler().load_from_string(self.body)
        self.xml = ET.fromstring(self.body)
        #self.xml_body = xml.dom.minidom.parseString(self.body)
        self.trace(3, 'xml type ' + str(type(self.xml)))
        
        
        if self.content_type.find('application/atom') >= 0:
            return self.parse_atom_feed()
        elif self.content_type.find('application/rss') >= 0:
            return self.parse_rss_feed()
        else:
            raise Exception('Content-type of feed is ' + content_type + '. Not handled!')



    def parse_atom_feed(self):
        
        self.trace(7, 'xml type ' + str(type(self.xml)))
        self.trace(7, 'ls type' + str(type(['hej','hopp'])))

        assert(self.xml.tag.endswith('feed'))

        entries = self.xml.findall('atom:entry', ns)
        self.trace(7, 'Found %d entries in atom feed ' % len(entries))
        for r in entries:
            self.handle_atom_entry(r)
   
        return self.xml

    def parse_rss_feed(self, body):
        raise NotImplementedError()


    def handle_atom_entry(self, entryEl):
        #: type: entryEl: xml.etree.ElementTree.Element

        url = ''

        link = entryEl.find('atom:link/[@type="text/html"]', ns)
        if link is None:
            link = entryEl.find('atom:link', ns)
            link.attrib['type'] = "text/html"
        url = link.attrib['href']

        self.trace(6, 'url for entry ' + url)
        
        media_url = self.fetch_media_url_for_entry(url)

        media_link_el = xml.etree.ElementTree.Element('link', { 'rel':"self", 'href': media_url, 'type': 'audio/mp4' })
        entryEl.append(media_link_el)
        return entryEl

    def check_match_avsnitt_programid(self, url):
        return re.match('http.*avsnitt[/=]([^&/;?]+).*programid=([^&/;?]+)', url)

    def fetch_media_url_for_entry(self, url):
        m = self.check_match_avsnitt_programid(url)
        if m:
            avsnitt = m.group(1)
            programid = m.group(2)    
            url = 'http://leifdev.leiflundgren.com:8091/py-cgi/sr_redirect?avsnitt=' + avsnitt + ';programid=' + programid + ';tracelevel=' + str(self.tracelevel)
            self.trace(7, 'created sr_redirect url for avsnitt=' + avsnitt + ' and programid=' + programid +"\n" + url)
            return url

        self.trace(8, 'Processing ' + url)
        u_thing = urllib2.urlopen(urllib2.Request(url))
        content_type = u_thing.headers['content-type']
        if content_type.find(';') > 0:
            content_type = content_type[0:content_type.find(';')].strip()
        if content_type.find('text/html') < 0:
            self.trace(2, 'Content-type is "' + content_type + '". That was not expected!')

        if u_thing.geturl() != url:
            url = u_thing.geturl()
            self.trace(5, 'seems like redirect to ' + url)
            if self.check_match_avsnitt_programid(url):
                return self.fetch_media_url_for_entry(url)

        self.handle_sr_episode(url, u_thing.read())

        
 

    #def handle_sr_program_page(self, url):
    #    """ Handles download of latest episode from
    #        http://sverigesradio.se/sida/avsnitt?programid=4490
    #    """
    #    self.trace(6, 'handle_sr_program_page(' + url + ')' )
    #    response = urllib2.urlopen(url)
    #    html = response.read()
        
    #    pos = html.find('<span>Lyssna</span>')
    #    if pos < 0:
    #        raise 'SR program page lacks Lyssna-tag'
    #    self.trace(9, 'clip ' + str(pos) + ': ' + html[pos:pos+50])
        
    #    href= html.rfind('href="', 0, pos)
    #    if pos < 0:
    #        raise 'SR program page has, Lyssna-tag but href is missing'
    #    href = href + 6
    #    self.trace(9, 'href=' + html[href:href+50])
        
    #    endp = html.find('"', href)
    #    self.trace(9, 'href=' + str(href) + '  endp=' + str(endp))
    #    page_url = urllib.unquote(html[href:endp]).replace('&amp;', '&')
    #    self.trace(8, 'page_url: ' + page_url)
            
    #    # Create a list of each bit between slashes
    #    slashparts = url.split('/')
    #    # Now join back the first three sections 'http:', '' and 'example.com'
    #    basename = '/'.join(slashparts[:3])
    #    url = basename + page_url
    #    self.trace(4, 'Deduced latest episode to be ' + url)
        
    #    # raise 'abort!!!!'
        
    #    self.handle_sr_episode(url)
        
    #    #self.trace(0, 'we dont actualy do anything with the program page yet. We should find latest episode or something...')
    #    #exit()
        
    # http://sverigesradio.se/sida/avsnitt/412431?programid=4490
    def handle_sr_episode(self, url, response_html = None):
        self.trace(5, "looking at SR episode " + url)

        if not re.match('http://sverigesradio.se/sida/avsnitt/\d+\?programid=\d+&playepisode=\d+', url):
            m = re.match('http://sverigesradio.se/sida/avsnitt/(\d+)\?programid=\d+', url)
            if not m:
                assert("The URL seems to be missing the avsnitt-i: " + url)
            self.trace(7, 'deduced episodeid to be ' + m.group(1))
            
            return self.handle_sr_episode(url.rstrip('&') + '&playepisode=' + m.group(1), response_html)

        
        if response_html is None:
            response = urllib2.urlopen(url)
            response_html = response.read()

        # look for <meta name="twitter:player:stream" content="http://sverigesradio.se/topsy/ljudfil/5032268" />
        
        stream = self.find_html_meta_argument(response_html, 'twitter:player:stream')
        
        if not stream:
            raise Exception("Failed to find twitter:player:stream-meta-header!")
        
        if not stream.startswith('http'):
            stream = 'http://sverigesradio.se' + stream
            self.trace(5, 'modified stream url to ' + stream)
            
        if not self.filename:
            self.trace(8, 'Trying to deduce filename from response_html-content.')
            programname = ''
            displaydate = self.find_html_meta_argument(response_html, 'displaydate')
            programid = self.find_html_meta_argument(response_html, 'programid')

            # change date from 20141210 to 2014-12-10            
            displaydate =  displaydate[:-4] + '-' +  displaydate[-4:-2] + '-' + displaydate[-2:]

            title = self.find_html_meta_argument(response_html, 'og:title')

            idx = title.rfind(' - ')
            if idx < 0:
                self.trace(8, 'programname is not part of og:title, truing twitter:title')
                title = self.find_html_meta_argument(response_html, 'twitter:title')
                idx = title.rfind(' - ')

            if idx > 0:
                programname = title[idx+3:].strip()
                title = title[:idx]
  
            programname = common.unescape_html(programname)
            programname = programname.replace('/', ' ').rstrip(' .,!')
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

            self.filename = programname + ' ' + displaydate + ' ' + title + '.m4a'
            self.trace(4, 'filename: ' + self.filename)
            self.assertTargetDoesntExistOrOverwrite()


            #if programid == '4490':
            #    programname = 'Lexsommar'



        self.handle_url(stream)
            
    def handle_sr_laddaner(self, url):
        """
            Handles an URL of the form http://sverigesradio.se/topsy/ljudfil/5036246
            @type url: str
        """

        assert isinstance(url, str)

        self.trace(5, "looking at SR laddaner " + url)
         
        response = requests.get(url, allow_redirects=False)
        if  response.status_code == 302 or response.headers['Location'] != '':
            self.trace(6, "response "+ str(response.status_code) + ' Location: ' + response.headers['Location'])
            return self.handle_url(response.headers['Location'])
        

        raise "response "+ str(response.status_code) + "\nHad expected a 302 redirect to lyssnaigen.se.se"

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
        if os.path.splitext(self.filename)[1] != '.m4a':
            self.trace(5, 'Filename ' + self.filename + ' doesn\'t end with .m4a  SR files should do that, changing!')
            self.filename = os.path. os.path.splitext(self.filename)[0] + '.m4a'
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

        try:
            rkn = remove_kulturnytt.RemoveKulturnytt(self.filename, self.overwrite, self.tracelevel, True)
            new_files = rkn.main()
            self.trace(7, 'Kulturnytt removal done, parts: ' + str(new_files))
        except (OSError, e):
            if e.errno == errno.ENOENT:
                self.trace(4, 'Failed to launch ffmpeg. Ignoring splitting files.')
            else:
                raise e


        if new_files is None:
            new_files = [self.filename]

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

    def read_rss_file(self, rssfile):
        self.trace(6, 'Reading local rss file from ' + rssfile)
        feedparser = feedparser.parse(rssfile)
        self.trace(8, 'file read: ' + common.pretty(feedparser))


        
        
    def update_rss(self):
        self.trace(4, 'Updating local RSS file ' + self.rssfile)
        rss2 = self.rss_feed.format_rss2_string()
        self.trace(7, xml.dom.minidom.parseString(rss2).toprettyxml())

        with open(self.rssfile, "w") as text_file:
            text_file.write(rss2)
                   
        pass

    def source_is_show_number(self, x):
        return x.isdigit()

    def source_is_sr_show(self, x):
        # http://sverigesradio.se/sida/avsnitt?programid=4429
        return not re.match('http\://sverigesradio.se/sida/avsnitt\?programid=\d+$', x) is None

    def add_sr_show(self, sr_programid_url):
        # http://sverigesradio.se/sida/avsnitt?programid=4429
        m = re.match('http\://sverigesradio.se/sida/avsnitt\?.*programid=(\d+)', sr_programid_url)
        self.add_program('http://api.sr.se/api/rss/program/' + m.group(1))


    def source_is_http(self, x):
        return x.startswith('http')



class TestSrFetch(unittest.TestCase):
    pass

#args 4430 12 
if __name__ == '__main__':
    for a in sys.argv:
        if a.find('unittest') >= 0:
            sys.exit(unittest.main())


    if len(sys.argv) == 1 or sys.argv[1][0] == '-' and sys.argv[1].find('h') > 0:
        print(sys.argv[0] + ' feed_url / sr-programid [tracelevel=8]')
        sys.exit(0)

    feed_url = sys.argv[1] if sys.argv[1].find('http') == 0 else 'http://api.sr.se/api/rss/program/' + sys.argv[1]
    
    if len(sys.argv) >= 3:
        common.tracelevel = int(sys.argv[2])
    else:
        common.tracelevel = 8

    sr_feed = SrFeed(feed_url, common.tracelevel)


    feed = sr_feed.get_feed()
    
    print(feed)
             
     