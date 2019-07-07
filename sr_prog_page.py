#!/usr/bin/python3
###  # -*- codi   ng: iso-8859-1 -*-

import sys
import os
import unittest
import re
import sr_helpers
import datetime
import XmlHandler

from urllib.parse import urlparse

import Page2RSS
import argparse

#import ET.ElementTree 
import lxml.etree as ET
import lxml.html as EHTML

import common
from common import is_none_or_empty

from XmlHandler import get_namespace



def parse_find_a_playonclick(root: ET.ElementTree) -> str:
    a_play = XmlHandler.find_element_attribute(root, 'a', 'data-require', "modules/play-on-click")
    # if a_play is not None: return a_play.attrib['href'] 

    return None if a_play is None else a_play.attrib['href'] 


def parse_find_a__data_clickable_content(root: ET.ElementTree) -> str:
    a_play = XmlHandler.find_element_attribute(root, 'a', 'data-clickable-content', "link")
    # if a_play is not None: return a_play.attrib['href'] 

    return None if a_play is None else a_play.attrib['href'] 

""" 
    Find Sändes-keyword and extract time from that.
"""

def parse_find_transmit_time(root: ET.ElementTree, date_today:datetime) -> datetime:

    if date_today is None:
        raise ValueError("date_today not specified!")
    html = ET.tostring(root, pretty_print=True)
    for meta in XmlHandler.findall_element_attribute(root, 'div', 'class', "audio-heading__meta"): # <div class="audio-heading__meta">
        for span in XmlHandler.findall_element_attribute(meta, 'span', 'class', "metadata-item-text"): # <span class="metadata-item-text">ons 19 sep kl 17:06</span>
            try:
                txt = span.text
                if txt.startswith('kl ') or txt.find(' kl ') > 0:
                    return sr_helpers.parse_sr_time_string(txt, date_today)
            except ValueError:
                pass

            
    for span in XmlHandler.findall_element_attribute(root, 'span', 'class', 'date'):
        try:
            abbr = span.find('abbr[@title]')
            return sr_helpers.parse_sr_time_string(abbr.attrib['title'], date_today)
        except ValueError:
            pass
    for span in XmlHandler.findall_element_attribute(root, 'span', 'class', 'tiny-text'):
        # 2nd attempt, check text-context                
        try:
            if span.text.find('S&#228;ndes') >= 0 or span.text.find('S\xe4ndes') >= 0:
                abbr = span.find('abbr[@title]')
                return sr_helpers.parse_sr_time_string(abbr.attrib['title'], date_today)
        except ValueError:
            pass
    return None



def parse_find_title(root: ET.ElementTree) -> str:

    # Sample from 2018-09-22
    # <div class="audio-heading__title">
    #        <a  href="/avsnitt/1153306" data-clickable-content="link" class="heading" >Luftens dag!</a>
    #        <div class="audio-heading__meta">
    #                <div class="audio-heading__meta-item">
    #                    <abbr title="114 minuter">114 min</abbr>
    #                </div>
    #                <div class="audio-heading__meta-item">
    #                    <span class="metadata-item-text">-</span>
    #                </div>
    #                <div class="audio-heading__meta-item">
    #                    <span class="metadata-item-text">ons 19 sep kl 17:06</span>
    #                </div>
    #        </div>
    #</div>
    try:
        episode_body = XmlHandler.find_element_attribute(root, 'div', 'class', "audio-heading__title")
        episode_a_href = XmlHandler.find_element_attribute(episode_body, 'a', 'class', "heading")

        return episode_a_href.text_content().strip()
    except AttributeError:
        pass

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
    # <div class="latest-episode__playimage">
    try:
        episode_body = XmlHandler.find_element_attribute(root, 'div', 'class', "episode*-body")
        episode__content = XmlHandler.find_element_attribute(episode_body, 'div', 'class', "*episode__content")
        title_span = XmlHandler.find_element_attribute(episode__content, 'span', 'class', "screen-reader-description")
        return title_span.text_content().strip()
    except AttributeError:
        pass

    try:
        episode_body = XmlHandler.find_element_attribute(root, 'div', 'class', "episode-list__item__title")
        episode_a_href = XmlHandler.find_element_attribute(episode_body, 'a', 'class', "heading heading--small")

        return episode_a_href.text_content().strip()
    except AttributeError:
        pass

    # <svg class="play-icon-play-pause" (which is inside a-href-tag)
    tag = XmlHandler.find_element_attribute(root, 'svg', 'class', "play-icon-play-pause")
    while tag:
        if tag.tag == 'a':
            return tag.attrib.get('aria-label')

    common.trace(8, 'Failed to find a title in div \n', ET.tostring(root, pretty_print=True))

    return None


def parse_find_desc(div: ET.ElementTree) -> str: 
    while True:

        try:
            audio_episode_body = XmlHandler.find_element_attribute(div, 'div', 'class', "audio-episode-body")
            p = XmlHandler.find_element_attribute(audio_episode_body, 'p', 'class', "*preamble")
            if p:
                return p.text_content().strip()
        except AttributeError:
            pass            

        try:
            audio_audiobox_body = XmlHandler.find_element_attribute(div, 'div', 'class', "audio-box-body")
            p = XmlHandler.find_element_attribute(audio_audiobox_body, 'p', 'class', "preamble")
            return p.text_content().strip()
        except AttributeError:
            pass

        try:
            episode_body = XmlHandler.find_element_attribute(div, 'div', 'class', "episode*-body")
            episode__content = XmlHandler.find_element_attribute(episode_body, 'div', 'class', "*episode__content")
            episode__body = XmlHandler.find_element_attribute(episode__content, 'div', 'class', "*episode__body")
            if episode__body is not None:
                p = XmlHandler.find_first_child(episode__body, 'p')
                el = p if p is not None else episode__body
                return el.text_content().strip()
        except AttributeError:
            pass

        try:
            ep_desc = XmlHandler.find_element_attribute(div, 'div', 'class', "episode-list*item*description*" )
            desc = ep_desc.text_content().strip()
            if len(desc) > 0:
                return desc
        
            p = XmlHandler.find_element_attribute(audio_audiobox_body, 'p', 'class', "text*")
            return p.text_content().strip()
        except AttributeError:
            pass

        try:
            ep_desc = XmlHandler.find_element_attribute(div, 'div', 'class', 'latest-episode__preamble ltr' )
            desc = ep_desc.text_content().strip()
            if len(desc) > 0:
                return desc
        
            p = XmlHandler.find_element_attribute(audio_audiobox_body, 'p', 'class', "text*")
            return p.text_content().strip()
        except AttributeError:
            pass

        parent_div = div.getparent()
        parent_class = parent_div.attrib['class']
        if not parent_class is None and not parent_class.startswith("episode-list-item"):
            common.trace(3, 'div has class "' + parent_class + '", not have class episode-list-item*, failed to find content')
            return None

        div = parent_div
        # next loop


def parse_find_episode_url(el: ET.ElementTree) -> (str, str) :
    a_ep = XmlHandler.find_element_attribute(el, 'a', 'href', '/sida/avsnitt/*')
    if a_ep is None:
        return (None, None)
    return ( a_ep.attrib['href'], a_ep.text_content() )


class SrProgramPageParser(object):

    def __init__(self, tracelevel, html_dom = None, program_prefix = ''):
        assert isinstance(tracelevel, int), 'tracelevel'
        assert html_dom is None or isinstance(html_dom, ET._ElementTree) or isinstance(html_dom, EHTML.HtmlEntity), 'html_dom was ' + type(html_dom).__name__
        assert isinstance(program_prefix, str), 'program_prefix should be string'

        self.trace(5, 'html_dom is ' + type(html_dom).__name__)
        # self.trace(9, ET.tostring(html_dom, pretty_print=True, encoding='unicode'))
        
        self.tracelevel = tracelevel
        self.url_ = None
        self.program_prefix = program_prefix
        self.episodes_ = None
        self.html_ = html_dom
        # page_parser.html = self.html_


    @property
    def url(self):
        return self.url_

    @url.setter
    def url(self, value):
        self.url_ = value
        self.fetch_page(self.url_)

    @property
    def html_text(self):
        return ET.tostring(self.html_, pretty_print=True).decode('utf-8')

    @property
    def html(self):
        return self.html_

    @html.setter
    def html(self, value):
        try:
            if isinstance(value, str):
                self.html_ = EHTML.parse(value)
            elif isinstance(value, ET._ElementTree):
                self.html_ = value
            else:
                raise ValueError('html set to unknown type: ' + str(type(value)))
            self.trace(9, 'got page \r\n', self.html)
        except Exception as ex:
            self.trace(5, 'Failed to parse html: ', ex)
            raise

    @property
    def timestamp(self):
        m = None
        for e in self.episodes_:
            if m is None or m < e['timestamp']:
                m = e['timestamp']
        return m

    def trace(self, level, *args):
        common.trace(level, 'SrProgramPageParser: ', args)


    def fetch_page(self, url):
        self.trace(5, 'fetching ' + url)
        self.html = EHTML.parse(url)
        self.trace(9, 'got page \r\n', ET.tostring(self.html, pretty_print=True))
        #print ET.tostring(self.html, pretty_print=True)


    def parse_page(self):

        # good links are 
        # <a href="/sida/avsnitt/587231?programid=2480&amp;playepisode=587231" aria-label="Lyssna(161 min)" class="btn btn-solid play-symbol play-symbol-wide play" data-require="modules/play-on-click">&#13;
        # <a href="/sida/avsnitt/587242?programid=2480" class="btn2 btn2-image btn2-image-foldable" data-require="modules/play-on-click">

        self.episodes_ = []

        # for timestamp_span in self.html.find('span class="page-render-timestamp hidden" data-timestamp="2015-07-28 19:11:25" />&#13;
        html_timestamp = datetime.datetime.today()
        timestamp_span = self.html.find('//span[@class="page-render-timestamp hidden"]')
        if not timestamp_span is None:
            html_timestamp = common.parse_datetime(timestamp_span.attrib['data-timestamp'])


        html_root = self.html.getroot()
        head = html_root[0]

        author_meta = head.find('meta[@name="author"]')        
        self.author = '' if author_meta is None else author_meta.attrib['content']

        description_meta = head.find('meta[@name="description"]')        
        self.description = '' if description_meta is None else description_meta.attrib['content']

        keywords_meta = head.find('meta[@name="keywords"]')        
        self.title = '' if keywords_meta is None else keywords_meta.attrib['content']

        title = head.find('title')
        if not title is None:
            self.title = title.text
              
        prefix = 'Alla avsnitt'
        postfix = 'Sveriges Radio'
        trims = '|- '
        if self.title.startswith(prefix):
            self.title = self.title[len(prefix):]
        if self.title.endswith(postfix):
            self.title = self.title[:-len(postfix)]
        self.title = self.title.strip(trims)
        
        if self.program_prefix:
            self.title = self.program_prefix + ' - ' + self.title
            self.trace(7, 'After adding program_prefix title became ' + self.title)
           
  
        logo_meta = XmlHandler.find_element_attribute(head, 'meta', 'name', "*:image")        
        if logo_meta is None:
            logo_meta = XmlHandler.find_element_attribute(head, 'meta', 'property', "*:image")
        self.logo = '' if logo_meta is None else logo_meta.attrib['content']


                      
        self.lang = self.html.getroot().attrib.get('lang', '')

        # episodeExplorerRoot = self.html.find('//div[@class="episode-explorer__list"]')
        # episodeExplorerRoot = self.html.find('//div[@class="episode-list-item th-p2 th-override"]')
        divs_to_search = XmlHandler.findall_element_attribute(self.html.getroot(), 'div', 'class', 'episode-list-item__content')
        if len(divs_to_search) == 0:
            divs_to_search = XmlHandler.findall_element_attribute(self.html.getroot(), 'div', 'class', 'episode-list-item *')

        # divs_to_search = XmlHandler.findall_element_attribute(episodeExplorerRoot, 'div', 'class', "episode-list-item__header")
        #for hpath in [
        #    '//div[@class="episode-latest-body"]',
        #    '//div[@class="audio-box-content"]',
        #    '//div[@class="audio-episode-content"]',
        #    '//div[@class="episode-list-item__info-teop"]',
        #    '//div[@class="episode-list__item__title"]',
        #    '//div[@class="audio-heading__title"]',
        #    ]:
        #    divs = self.html.findall(hpath)
        #    if len(divs) == 0:
        #        self.trace(7, 'at ' + hpath + ' nothing found')
        #    else:
        #        self.trace(7, 'at ' + hpath + ' found ', len(divs), ' things')
        #        divs_to_search.extend(divs)

        if len(divs_to_search) == 0:
            self.trace(3, 'When searching the HTML page, nothing found')


        for div in divs_to_search:
            avsnitt = self.parse_episode(div, html_timestamp)
            if avsnitt is None: continue 
            
            self.episodes_.append(avsnitt)
            
        self.validate_episodes()

        return self.episodes_

    def parse_episode(self, div, html_timestamp):
        if div is None or len(div)==0:
            return None

        avsnitt_title = ''

        a_href = parse_find_a_playonclick(div)

        if a_href is None:
            a_href = parse_find_a__data_clickable_content(div)
        
        if a_href == '#':
            # we have found a block like below. Neet to find the 2nd a-href element. 
            #<div class="episode-list-item__info-top">
            #    <div class="episode-list-item__play">
            #        <a  href="#" data-audio-type="episode" data-audio-id="819043" data-require="modules/play-on-click" class="play-symbol play-symbol--circle" ><span class="sr-icon" ><i class="play-arrow play-arrow--medium sr-icon__image" ></i></span></a>
            #    </div>
            #    <div class="episode-list-item__header">
            #        <a  href="/sida/avsnitt/819043?programid=4429" class="heading__d heading--inverted line-clamp heading__d-line-clamp--2" >R&#246;ster under himlen</a>
            #    </div>
            #</div>            
            (a_href, avsnitt_title) = parse_find_episode_url(div)

        if a_href is None:
            d2 = XmlHandler.find_element_attribute(div, 'div', 'class', 'audio-heading__title')
            if not d2 is None:
                a_el = XmlHandler.find_element_attribute(d2, 'a', 'data-clickable-content', 'link')
                if not a_el is None:
                    a_href = a_el.attrib['href']
                    avsnitt_title = a_el.text

        if a_href is None:
            self.trace(7, "Failed to find playonclick on \n" + ET.tostring(div, encoding='unicode', pretty_print=True) )
            return None

        url = urlparse(a_href)
        path_parts = url.path.split('/')
            
        if len(path_parts) < 3 or path_parts[-2] != 'avsnitt':
            return None

                
        avsnitt_id = path_parts[-1]

        avsnitt_timestamp = parse_find_transmit_time(div, html_timestamp)
        if avsnitt_timestamp is None:
            avsnitt_timestamp = parse_find_transmit_time(div.getparent(), html_timestamp)
        if avsnitt_timestamp is None:
            self.trace(3, 'Failed to find transmit time for ' + str(avsnitt_id) + 'in \n', ET.tostring(div.getparent(), pretty_print=True))
            raise ValueError('Failed to find transmit time for ' + str(avsnitt_id))

        if not avsnitt_title:
            avsnitt_title = parse_find_title(div)

        avsnitt_description = parse_find_desc(div)

        avsnitt = next((e for e in self.episodes_ if e['avsnitt'] == avsnitt_id), None)
        if avsnitt is None:
            avsnitt = {'avsnitt': avsnitt_id }

        if not avsnitt_timestamp is None:
            avsnitt['timestamp'] = avsnitt_timestamp

        if  avsnitt_title:
            avsnitt['title'] = avsnitt_title
        if avsnitt_description:
            avsnitt['description'] = avsnitt_description
            if not avsnitt_title:
                avsnitt['title'] = avsnitt_description

        logo_meta = XmlHandler.find_element_attribute(div, 'meta', 'name', "*:image")        
        if logo_meta is None:
            logo_meta = XmlHandler.find_element_attribute(div, 'meta', 'property', "*:image")
        avsnitt['logo'] = '' if logo_meta is None else logo_meta.attrib['content']
        if logo_meta is None:
            logo_meta = XmlHandler.find_element_attribute(div, 'img', 'class', "episode-list-item__image")
            if not logo_meta is None:
                avsnitt['logo'] = logo_meta.attrib['src']


        self.validate_one_episode(avsnitt)
        return avsnitt


    def validate_episodes(self):
        for avsnitt in self.episodes_:
            self.validate_one_episode(avsnitt)

    def validate_one_episode(self, avsnitt):
        avsnitt_id = avsnitt['avsnitt']
            
        if not 'timestamp' in avsnitt:
            msg = "When parsing avsnitt " + str(avsnitt_id) + ", failed to find timestamp"
            self.trace(2, msg)
            raise ValueError('Bad parse-data: ' + msg)
        if not 'title' in avsnitt:
            msg = "When parsing avsnitt " + str(avsnitt_id) + ", failed to find title"
            self.trace(2, msg)
            raise ValueError('Bad parse-data: ' + msg)


    def find_episodes(self):
        if self.html_ is None:
            self.fetch_page(self.url)
        return self.parse_page()
        
    def episodes(self):
        if self.episodes_ is None:
            self.find_episodes()        
        return self.episodes_
    


def get_root(element_thing):
    # lET._ElementTree :: getroot
    if isinstance(element_thing, ET._ElementTree):
        return element_thing.getroot()
    # <type 'lET._Element'> :: getroottree
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
    parser.add_argument('--url', help='use url rather than deduce from progid', default=None, required=False)

    r = parser.parse_args(None)

    common.tracelevel = r.tracelevel
    
    parser = SrProgramPageParser(common.tracelevel)
    parser.url = r.url
    episodes = parser.episodes()
    common.trace(3, 'SrProgramPageParser: result: ' , sorted(episodes, key=lambda ep: ep['avsnitt']))
    common.trace(5, 'newest episode ', parser.timestamp)
    
