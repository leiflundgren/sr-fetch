
# -*- coding: iso-8859-1 -*-


import common
import urllib2
import re
import datetime
import time
import unittest
import sys

def trace(level, *args):
    common.trace(level, 'sr_helpers: ', args)


def source_is_show_number(x):
    return x.isdigit()

def source_is_sr_show(x):
    # http://sverigesradio.se/sida/avsnitt?programid=4429
    return not re.match(r'http\://sverigesradio.se/sida/avsnitt\?programid=\d+$', x) is None


 
def find_html_meta_argument(html, argname):
    idx = html.find('<meta name="' + argname + '"')
    if idx < 0:
        idx = html.find('<meta property="' + argname + '"')
    if idx < 0:
        trace(6, "Failed to find meta-argument " + argname)
        return None
        
    # trace(8, 'found ' + html[idx:idx+200])
        
    idx = html.find('content=', idx)
    if idx < 0:
        trace(6, "Failed to find content-tag for meta-argument " + argname)
        return None
        
    begin = html.find('"', idx)
    if begin < 0:
        raise ValueError("Failed to find content-tag start quote")
            
    begin = begin+1
    end = html.find('"', begin)
    if end < 0:
        raise ValueError("Failed to find content-tag end quote")
            
    val = html[begin:end]
    trace(7, "value of "+ argname + " is '" + val + "'")
    return val

def find_html_link_argument(html, rel_type="canonical", pos = 0):
    while True:
        pos = html.find('<link ', pos)
        if pos < 0:
            trace(6, "Failed to find link element start pos ", str(pos))
            return None

        pos += 5
        endp = SrUrlFinder.find_html_endtag(html, 'link', pos)

        (rel_attrib, a_endp) = SrUrlFinder.find_html_attribute(html, 'rel', pos, endp)
        if rel_attrib != rel_type:
            trace(5, 'Failed to find <link rel="' + rel_type + '" in range ' + str(pos) + '--' + str(endp) )
            continue

        (href_attrib, a_endp) = SrUrlFinder.find_html_attribute(html, 'href', pos, endp)
        if rel_attrib is None:
            trace(5, 'Failed to find <link rel="' + rel_type + '" href="..." in range ' + str(pos) + '--' + str(endp) )
            continue

        return href_attrib


def urllib_open_feed(url):
    u_request = urllib2.Request(url, headers={"Accept" : "application/atom+xml, application/rss+xml, application/xml, text/xml, text/html"})
    return urllib2.urlopen( u_request )

def filename_from_html_content(html):
    trace(8, 'Trying to deduce filename from html-content.')
    programname = ''
    displaydate = find_html_meta_argument(html, 'displaydate')
    programid = find_html_meta_argument(html, 'programid')

    # change date from 20141210 to 2014-12-10            
    displaydate = displaydate[:-4] + '-' +  displaydate[-4:-2] + '-' + displaydate[-2:]

    title = find_html_meta_argument(html, 'og:title')

    idx = title.rfind(' - ')
    if idx < 0:
        trace(8, 'programname is not part of og:title, truing twitter:title')
        title = find_html_meta_argument(html, 'twitter:title')
        idx = title.rfind(' - ')

    if idx > 0:
        programname = title[idx+3:].strip()
        title = title[:idx]
  
    programname = common.unescape_html(programname)
    programname = programname.replace('/', ' ').rstrip(' .,!')
    if programname == 'Lordagsmorgon i P2':
        programname = 'Lordagsmorgon'
    trace(7, 'programname is ' + programname)


    parts = title.split(' ')

    # trim date/time from end
    lastToKeep = 0
    for idx in range(0, len(parts)):
        # trace(9, 'idx=' + str(idx) + ': "' + parts[idx] + '"')
        if  (
                not re.match(r'\d+(:\d+)*', parts[idx]) # skip time like 12:24:00
                and parts[idx] != 'kl'
                and not common.is_swe_month(parts[idx])
                and not common.is_swe_weekday(parts[idx])
            ):
            #trace(9, 'idx=' + str(idx) + ' is to keep "' + parts[idx] + '"')                    
            lastToKeep = idx
        #trace(9, 'skipping idx=' + str(idx) + ' "' + parts[idx] + '" from title')

    if lastToKeep == 0:
        trace(4, 'didn\'t find any valid name-parts in title. Keeping as is: "', title, '"')
    else:
        title = ' '.join(parts[0:lastToKeep+1])

    title = common.unescape_html(title)
    title = title.replace('/', ' ').strip(' .,!')

    trace(4, 'new title is ' + title + '\r\skipped index ', lastToKeep, 'to ', len(parts)-1)

    filename = programname + ' ' + displaydate + ' ' + title + '.m4a'
    trace(4, 'filename: ' + self.filename)
        
    return filename

def parse_sr_time_string(s, today):
    """ 
        This method tries to handle strings like
            klockan 10:03
            igår
            tisdags
            fredag 24 juli klockan 10:03
    """
    trace(8, 'parse_sr_time_string(' + s + ')')
    t = today

    parts = s.strip().split(' ')

    i=0
    while i<len(parts):
        if parts[i] == 'klockan' and i+1<len(parts):
            n = parts[i+1].split(':')
            hour = int(n[0])
            minute = int(n[1]) if len(n) > 1 else 0
            second = int(n[2]) if len(n) > 2 else 0
            t = datetime.datetime.combine(t.date(), datetime.time(hour, minute, second))
            i += 2
        elif parts[i] == 'Ig&#229;r' or parts[i] == u'Ig\xe5r':
            t -= datetime.timedelta(days=1)
            i += 1
        elif common.is_swe_weekday(parts[i]):
            #ignore weekday
            i += 1
        elif len(parts[i]) == 4 and parts[i].isdigit():
            t = datetime.datetime(int(parts[i]), t.month, t.day, t.hour, t.minute, t.second)
            i += 1                                  
        elif i+1 < len(parts) and parts[i].isdigit() and common.is_swe_month(parts[i+1]):
            month = common.parse_swe_month(parts[i+1])
            day = int(parts[i])
            t = datetime.datetime(t.year, month, day, t.hour, t.minute, t.second)
            if t > today: # if date causes wrap-around of year
                t = t - datetime.timedelta(365)

            i += 2
        else:
            raise ValueError('parse_sr_time_string: Unhandled part ' + parts[i])

    trace(8, 'parse_sr_time_string --> ' + str(t))
    return t
    


class TestHelpers(unittest.TestCase):
    def test_parse_sr_time_string(self):

        t = parse_sr_time_string('klockan 10:03') # Just check no exception

        base_day = datetime.datetime(2015,7,29)

        self.assertEqual(datetime.datetime(2015,7,29, 10,3,0), parse_sr_time_string('klockan 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,28, 10,3,0), parse_sr_time_string('Ig&#229;r klockan 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,24, 10,3,0), parse_sr_time_string('fredag 24 juli klockan 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,24, 10,3,0), parse_sr_time_string('m&#229;ndag 24 juli klockan 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,24, 10,3,0), parse_sr_time_string(u'söndag 24 juli klockan 10:03', base_day))
    pass

if __name__ == '__main__':
    sys.exit(unittest.main(argv=['-v']))
