xml_loaded = False
xml_minidom = False
xml_lxml = False 

if not xml_loaded:
    try:
        import lxml.etree
        xml_loaded=True
        xml_lxml = True
    except ImportError:
        pass

if not xml_loaded:
    try:
        import xml.dom.minidom
        xml_loaded=True
        xml_minidom = True
    except ImportError:
        pass


if not xml_loaded:
    raise Exception('Failed to load *ANY* XML library!!!')

class XmlHandler(object):
    """description of class"""

    def load_from_string(self, str):
        if xml_minidom:
            return self.load_from_string_minidom(str)
        elif xml_lxml:
            return self.load_from_string_lxml(str)
        else:
            raise Exception('No XMl handler loaded')

    def load_from_string_minidom(self, s):
        if isinstance(s, str):
            self.xml = xml.dom.minidom.parseString(s)
        elif isinstance(s, unicode):
            self.xml = xml.dom.minidom.parseString(s.encode('utf-8'))
        else:
            raise Exception('unknown string  type ' + str(type(s)))

    def load_from_string_lxml(self, str):
        self.xml = lxml.etree.fromstring(str)




