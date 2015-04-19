import common
from common import trace
from common import tracelevel
import unittest
import sys

xml_loaded = False
xml_minidom = False
xml_lxml = False 
xml_cxml = False
xml_exml = False


try:
    import xml.etree.CElementTree
    x = xml.etree.cElementTree.fromstring('<hello target="World">there</hello>') 
    xml_loaded=True
    xml_cxml = True
except ImportError:
    pass

try:
    import xml.etree.ElementTree
    x = xml.etree.ElementTree.fromstring('<hello target="World">there</hello>') 
    xml_loaded=True
    xml_exml = True
except ImportError:
    pass

try:
    import lxml.etree.ElementTree
    x = lxml.etree.ElementTree.fromstring('<hello target="World">there</hello>') 
    xml_loaded=True
    xml_lxml = True
except ImportError:
    pass

try:
    import xml.dom.minidom
    x = xml.dom.minidom.parseString('<hello target="World">there</hello>') 
    xml_loaded=True
    xml_minidom = True
except ImportError:
    pass

if not xml_loaded:
    raise Exception('Failed to load *ANY* XML library!!!')


       

class XmlHandler(object):
    """description of class"""

    def load_from_string(self, string):
        if xml_cxml:
            self.xml = xml.etree.CElementTree.fromstring(string)
        elif xml_exml:
            self.xml = xml.etree.ElementTree.fromstring(string)
        elif xml_lxml:
            self.xml = lxml.etree.ElementTree.fromstring(string)
        elif xml_mindom:
            self.xml = xml.dom.minidom.fromstring(string)
        else:
            raise Exception('Failed to load *ANY* XML library!!!')
        return self.xml
    
    def load_from_string_minidom(self, s):
        if isinstance(s, str):
            self.xml = xml.dom.minidom.parseString(s)
        elif isinstance(s, unicode):
            self.xml = xml.dom.minidom.parseString(s.encode('utf-8'))
        else:
            raise Exception('unknown string  type ' + str(type(s)))

    def load_from_string_cxml(self, s):
        self.xml = ET(s)


    def load_from_string_lxml(self, str):
        self.xml = lxml.etree.fromstring(str)

def find_child_nodes(el, node_names):
    #: :type el: xml.etree.ElementTree.Element
    #: :type node_names: list
                        
    trace(7, 'xml type ' + str(type(el)))


    if len(node_names) == 0:
        return [el]
    name = node_names[0]
    # if name[0] == '@':


    res = []
    #sub = el.
    for c in el:
        tag = c.tag
        #print tag

        # Ignore namespace if not specifed in query
        if tag[0] == '{' and name[0] != '{':
            tag = tag[tag.index('}')+1:]

        if tag == name:
            res = res + find_child_nodes(c, node_names[1:] )
    return res


class TestXmlHandler(unittest.TestCase):
    def test_xml_load(self):
        string = '<hello target="World">there</hello>'
        xml = XmlHandler().load_from_string(string)
        print 'got xml object ' + str(xml) + ' of type ' + str(type(xml))

    pass

if __name__ == '__main__':
    for a in sys.argv:
        if a.find('unittest') >= 0:            
            common.tracelevel = 8
            sys.argv = ['-v']
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
             
