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

    xml = None

    def __init__(self, string=None):
        if not string is None:
            self.xml = self.load_from_string(string)
             
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

def find_first_child(el, node_names):
    return find_child_nodes(el, node_names, True)

def find_child_nodes(el, node_names, only_first = False):

    #: :type el: xml.etree.ElementTree.Element
    #: :type node_names: list
                        
    if isinstance(node_names , str):
        return find_child_nodes(el, node_names.split('/'), only_first)

    # trace(7, 'xml type ' + str(type(el)))
    if len(node_names) == 0:
        return el
    name = node_names[0]
    if name[0] == '@':
        aname = name[1:]
        for n,v in el.attrib.iteritems():
            if n[0] == '{' and aname[0] != '{':
                n= n[n.index('}')+1:]

            if n==aname:
                return v
        return None

    if name[0] == '[':
        pass

    if name == 'text()':
        return el.text

    res = []
    #sub = el.
    for c in el:
        tag = c.tag
        #print tag

        # Ignore namespace if not specifed in query
        if tag[0] == '{' and name[0] != '{':
            tag = tag[tag.index('}')+1:]

        if tag == name:
            res.append(find_child_nodes(c, node_names[1:], only_first))
            if only_first and len(res) > 0:
                return res[0]
            
    return res


class TestXmlHandler(unittest.TestCase):
    def test_xml_load(self):
        string = '<xml_ex><hello target="World"><foo><bar>fubar</bar></foo> there</hello></xml_ex>'
        xml = XmlHandler().load_from_string(string)
        print 'got xml object ' + str(xml) + ' of type ' + str(type(xml))
                
        hello_ls = find_child_nodes(xml, ['hello'])
        self.assertEqual(1, len(hello_ls))

        foo = find_first_child(xml, 'hello/foo')
        self.assertEqual('foo', foo.tag)

        fubar = find_first_child(xml, 'hello/foo/bar/text()')
        self.assertEqual('fubar', fubar)
        world = find_first_child(xml, 'hello/@target')
        self.assertEqual('World', world)
    pass

if __name__ == '__main__':
    common.tracelevel = 8
    sys.argv = ['-v']
    sys.exit(unittest.main())

