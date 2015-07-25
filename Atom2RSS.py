#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import lxml.etree as ET
from common import trace
from common import pretty
from common import get_el

class Atom2RSS(object):
    """Converts an atom feed to an rss. Abstract base"""

    def __init__(self, *args, **kwargs):
        return super(Atom2RSS, self).__init__(*args, **kwargs)

    pass

class Atom2RssXsl(Atom2RSS):
    """Converts an atom feed to an rss using XSL"""
    
    xsl_http_url = 'http://atom.geekhood.net/atom2rss.xsl'
    xsl_file_path = 'atom2rss.xsl'

    def __init__(self, bGetFromNet):
        if bGetFromNet:
            trace(6, 'Loading xsl from ', self.xsl_http_url)
            self.xslt = ET.parse(self.xsl_http_url)
        else:
            trace(6, 'Loading xsl from ', self.xsl_file_path)
            self.xslt = ET.parse(self.xsl_file_path)
        self.transformer = ET.XSLT(self.xslt)
        trace(8, 'xsl loaded and transformer created: ' , self.transformer)

    def transform(self, atom_thing):
        trace(8, 'transforming atom_thing: ', str(type(atom_thing)))
        trace(8, 'transforming atom_thing: ', dir(atom_thing))

        #if True or isinstance(atom_thing, ET._Element):
        #    atom_thing = atom_thing.getroottree()
        #    trace(8, 'transfroming atom_thing: ', str(type(atom_thing)))
        # atom_thing = atom_thing.getroot()

        return self.transformer(atom_thing)

class Atom2RssNodePerNode(Atom2RSS):


    def __init__(self):
        return super(Atom2RssNodePerNode, self).__init__()

    def transform(self, atom_tree):
        """
        @atom_tree: ElementTree
        """
        if False: atom_tree = ET.ElementTree()

        ns = 'http://www.w3.org/2005/Atom'
        ns_xml = 'http://www.w3.org/XML/1998/namespace'

        nsmap = {None: ns, 'xml': ns_xml }
        nsxpath = {'a':ns, 'xml': ns_xml }
        atom_root = atom_tree.getroot()

        try:
            lang = atom_root.attrib['{http://www.w3.org/XML/1998/namespace}lang']
        except:
            lang = atom_root.attrib['lang']
        
        rss_root = ET.Element('rss', version='2.0')
        rss_channel = ET.SubElement(rss_root, 'channel')

        atom_title = atom_root.get('title')
        atom_title = atom_root.get('title', nsmap)
        atom_title = atom_root[0]
        atom_title = get_el(atom_root, 'title', ns)
        rss_title = ET.SubElement(rss_channel, 'title')
        rss_title.text = atom_title.text
        rss_title.text = atom_root.xpath('a:title/text()', namespaces=nsmap)


        

        # atom
        #<title type="text">P2 Live</title>
        #<subtitle type="text">Sveriges bästa konserter inom klassisk musik, nutida musik, jazz, folk- och världsmusik</subtitle>
        #<id>uuid:f3f4f7ea-e0bf-404b-b58b-9eb781b101b6;id=37566</id>
        #<rights type="text">Copyright Sveriges Radio 2015. All rights reserved.</rights>
        #<updated>2015-07-13T10:08:00+02:00</updated>
        #<logo>http://sverigesradio.se/sida/content/img/channellogos/srlogo.png</logo>
        #<link rel="alternate" href="http://sverigesradio.se/sida/default.aspx?programid=4427"/>

        # rss
        #<title>P2 Live</title>
        #<language>sv</language>
        #<description>Sveriges bästa konserter inom klassisk musik, nutida musik, jazz, folk- och världsmusik</description>
        #<image>
        #    <url>http://sverigesradio.se/sida/content/img/channellogos/srlogo.png</url>
        #    <title>P2 Live</title>
        #    <link>http://sverigesradio.se/sida/default.aspx?programid=4427</link>
        #</image>
        #<copyright>Copyright Sveriges Radio 2015. All rights reserved.</copyright>
        #<pubDate>2015-07-13T10:08:00+02:00</pubDate>
        #<link>http://sverigesradio.se/sida/default.aspx?programid=4427</link>
        
        return rss_root

if __name__ == '__main__':
    dom = ET.parse('sample.atom.xml')
    rss = Atom2RssNodePerNode().transform(dom)
    print ET.tostring(rss, pretty_print=True)
    pass