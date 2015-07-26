#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import lxml.etree as ET
from common import trace
from common import pretty
from common import get_el
from common import is_none_or_empty

from XmlHandler import find_first_child
from XmlHandler import find_child_nodes

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

        ns = 'http://www.w3.org/2005/Atom'
        ns_xml = 'http://www.w3.org/XML/1998/namespace'

        nsmap = {None: ns, 'xml': ns_xml }
        nsxpath = {'a':ns, 'xml': ns_xml }

        def getfirst(el, xp):
            r = get(el, xp)
            if len(r) > 0:
                return r[0]
            else:
                return ''

        def get(el, xp):
            return el.xpath(xp, namespaces=nsxpath)

        atom_root = atom_tree.getroot()

        
        r= getfirst(atom_tree, '/a:feed/a:rights[@type="text"]/text()')
        #r= get_first(atom_tree, '/a:feed/a:rights[@type="text"]/text()', namespaces=nsxpath)

        lang = getfirst(atom_tree, '/a:feed/@xml:lang')

#        lang = atom_tree.xpath('/a:feed/@xml:lang', namespaces=nsxpath)[0]
        
        rss_root = ET.Element('rss', version='2.0')
        rss_channel = ET.SubElement(rss_root, 'channel')

        rss_title = ET.SubElement(rss_channel, 'title')
        rss_title.text = getfirst(atom_root, 'a:title[@type="text"]/text()')

        ET.SubElement(rss_channel, 'language').text = lang
        
        ET.SubElement(rss_channel, 'description').text = getfirst(atom_root, 'a:subtitle[@type="text"]/text()')

        ET.SubElement(rss_channel, 'copyright').text = getfirst(atom_root, 'a:rights/text()')

        ET.SubElement(rss_channel, 'pubDate').text = getfirst(atom_root, 'a:updated/text()')


        rss_image = ET.SubElement(rss_channel, 'image')
        ET.SubElement(rss_image, 'url').text = getfirst(atom_root, 'a:logo/text()')
        ET.SubElement(rss_image, 'title').text = rss_title.text
        ET.SubElement(rss_image, 'link').text = getfirst(atom_root, 'a:link/@href')

        for atom_entry in find_child_nodes(atom_root, ['entry']):
            rss_item = ET.SubElement(rss_channel, 'item')
            atom_id = getfirst(atom_entry, 'a:id/text()')

            #rss
            #<item>
            ET.SubElement(rss_item, 'description').text = getfirst(atom_entry, 'a:summary/text()')
            ET.SubElement(rss_item, 'guid').text= atom_id
            ET.SubElement(rss_item, 'title').text= getfirst(atom_entry, 'a:title/text()')
            ET.SubElement(rss_item, 'pubDate').text= getfirst(atom_entry, 'a:published/text()')
            
            atom_href_link = getfirst(atom_entry, 'a:link[@type="text/html"]')
            href_link = ET.SubElement(rss_item, 'link', type="text/html")
            href_link.text= getfirst(atom_entry, 'a:link[@type="text/html"]/@href')
            trace(7, 'atom href ', ET.tostring(atom_href_link, pretty_print=True))
            
            atom_enclosure = getfirst(atom_entry, 'a:link[@rel="enclosure"]')            
#            if not atom_enclosure:
#                atom_enclosure = atom_entry[9]
            if not is_none_or_empty(atom_enclosure):
                try:
                    enclosure_link = ET.SubElement(rss_item, 'link', rel="enclosure")
                    enclosure_link.attrib['type'] =atom_enclosure.attrib.get('type','') 
                    enclosure_link.text= atom_enclosure.attrib['href']
                    trace(7, 'atom contained enclosure ', enclosure_link.text, ' type=', enclosure_link.attrib['type'])
                    trace(7, 'atom enclosure ', ET.tostring(atom_enclosure, pretty_print=True))
                    trace(7, 'rss enclosure ', ET.tostring(enclosure_link, pretty_print=True))
                except AttributeError, e:
                    trace(1, 'atom_enclosure="', atom_enclosure, '"')
                    raise
            else:
                trace(6, 'atom_entry ', atom_id, ' did not have enclosure: ', ET.tostring(atom_entry))

            ET.SubElement(rss_item, 'category').text = getfirst(atom_entry, 'a:category/text()')
            

        return rss_root

if __name__ == '__main__':
    dom = ET.parse('sample.atom.xml')
    rss = Atom2RssNodePerNode().transform(dom)
    print ET.tostring(rss, pretty_print=True)
    pass