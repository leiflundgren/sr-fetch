import lxml.etree as ET
from common import trace
from common import pretty

 
class Atom2RSS(object):
    """Converts an atom feed to an rss"""

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

if __name__ == '__main__':
    dom = ET.parse('sample.rss.xml')
    rss = Atom2RSS(False).transform(dom)
    print ET.tostring(rss, pretty_print=True)
    pass