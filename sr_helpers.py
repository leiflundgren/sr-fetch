
# coding: latin-1


import common
import urllib2
import re

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
    u_request = urllib2.Request(url, headers={"Accept" : "application/atom+xml, application/rss+xml, application/xml, text/xml"})
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
        if re.match(r'\d+(:\d+)*', parts[idx]):
            pass
        elif parts[idx] == 'kl':
            pass
        elif common.is_swe_month(parts[idx]):
            pass
        else:
            trace(9, 'idx=' + str(idx) + ' is to keep "' + parts[idx] + '"')                    
            lastToKeep = idx
            continue
        trace(9, 'skipping idx=' + str(idx) + ' "' + parts[idx] + '" from title')

    title = ' '.join(parts[0:lastToKeep+1])
    title = common.unescape_html(title)
    title = title.replace('/', ' ').strip(' .,!')

    trace(4, 'new title is ' + title)

    filename = programname + ' ' + displaydate + ' ' + title + '.m4a'
    trace(4, 'filename: ' + self.filename)
        
    return filename