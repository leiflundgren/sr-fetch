
# -*- coding: utf-8 -*-


import common
import urllib.request, urllib.error, urllib.parse
import re
import datetime
import unittest
import sys

def trace(level, *args):
    common.trace(level, 'sr_helpers: ', args)


def source_is_show_number(x):
    return x.isdigit()

def source_is_sr_show(x):
    # https://sverigesradio.se/sida/avsnitt?programid=4429
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

# def find_html_link_argument(html, rel_type="canonical", pos = 0):
#     while True:
#         pos = html.find('<link ', pos)
#         if pos < 0:
#             trace(6, "Failed to find link element start pos ", str(pos))
#             return None

#         pos += 5
#         endp = SrUrlFinder.find_html_endtag(html, 'link', pos)

#         (rel_attrib, a_endp) = SrUrlFinder.find_html_attribute(html, 'rel', pos, endp)
#         if rel_attrib != rel_type:
#             trace(5, 'Failed to find <link rel="' + rel_type + '" in range ' + str(pos) + '--' + str(endp) )
#             continue

#         (href_attrib, a_endp) = SrUrlFinder.find_html_attribute(html, 'href', pos, endp)
#         if rel_attrib is None:
#             trace(5, 'Failed to find <link rel="' + rel_type + '" href="..." in range ' + str(pos) + '--' + str(endp) )
#             continue

#         return href_attrib


def urllib_open_feed(url):
    u_request = urllib.request.Request(url, headers={"Accept" : "application/atom+xml, application/rss+xml, application/xml, text/xml, text/html"})
    return urllib.request.urlopen( u_request )

def filename_from_html_content(html):
    trace(8, 'Trying to deduce filename from html-content.')
    programname = ''
    displaydate = find_html_meta_argument(html, 'displaydate')
    # programid = find_html_meta_argument(html, 'programid')

    # change date from 20141210 to 2014-12-10      
    if len(displaydate) == 8:
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

    trace(4, 'new title is ' + title + '\nskipped index ', lastToKeep, 'to ', len(parts)-1)

    filename = programname + ' ' + displaydate + ' ' + title + '.m4a'
    trace(4, 'filename: ' + filename)
        
    return filename

def parse_sr_time_string(s: str, today: datetime) -> datetime:
    """ 
        This method tries to handle strings like
            klockan 10:03
            igår
            tisdags
            fredag 24 juli klockan 10:03
            ons 19 sep kl 17:06
    """
    trace(8, 'parse_sr_time_string(' + s + ')')
    tomorrow = today + datetime.timedelta(days=1)
    year = today.year
    month = today.month
    day  = today.day
    hour = today.hour
    minute = today.minute
    second = today.second
 
    parts = s.strip().split(' ')
    i=0

    # if common.is_swe_weekday(parts[0]):
    #         #ignore weekday
    #         i += 1


    while i<len(parts):        
        p = parts[i]
        if (parts[i].casefold() == 'klockan' or parts[i].casefold() == 'kl' ) and i+1<len(parts):
            time_parts = []
            for p in parts[i+1:]:
                if len(p) <= 2:
                    time_parts.append(int(p))

                elif len(p) >= 4 and p[2].isdigit():
                    time_parts.append(int(p[0:2]))
                    time_parts.append(int(p[2:4]))
                    if len(p) == 6: 
                        time_parts.append(int(p[4:6]))

                else:
                    delim = p[2]
                    n = p.split(delim)

                    for d in n:
                        time_parts.append(int(d))

            hour = time_parts[0] if len(time_parts) > 0 else 0
            minute = time_parts[1] if len(time_parts) > 1 else 0
            second = time_parts[2] if len(time_parts) > 2 else 0
            break ## Assume string ends with time

        elif parts[i] == 'Ig&#229;r' or parts[i] == 'Ig\xe5r':
            day-=1
            i += 1
        elif common.is_swe_weekday(parts[i]):
            #ignore weekday
            i += 1
        elif len(parts[i]) == 4 and parts[i].isdigit():
            year = int(parts[i])
            i += 1                                  
        elif i+1 < len(parts) and parts[i].isdigit() and common.is_swe_month(parts[i+1]):
            day = int(parts[i])
            month = common.parse_swe_month(parts[i+1])

            i += 2
        else:
            raise ValueError('parse_sr_time_string: Unhandled part ' + parts[i])

    t = datetime.datetime(year, month, day, hour, minute, second)
    if t > tomorrow: # if date causes wrap-around of year
        year -= 1
        t = datetime.datetime(year, month, day, hour, minute, second)

    trace(8, 'parse_sr_time_string --> ' + str(t))
    return t
    

if __name__ == '__main__':
    sys.exit(unittest.main(argv=['-v', 'sr_helpers_tests.py']))
    