import lxml.etree as ET
import codecs
from common import trace


class Atom2RSS(object):
    """Converts an atom feed to an rss"""

    xsl_http_url = 'http://atom.geekhood.net/atom2rss.xsl'
    xsl_file_path = 'atom2rss.xsl'

    def __init__(self, bGetFromNet):
        if bGetFromNet:
            trace(6, 'Loading xsl from ', xsl_http_url)
            self.xslt = ET.parse(xsl_http_url)
        else:
            trace(6, 'Loading xsl from ', xsl_file_path)
            self.xslt = ET.parse(xsl_file_path)
        self.transformer = ET.XSLT(xslt)
        trace(8, 'xsl loaded and transformer created: ' , self.transformer)

    def transform(self, atom_thing):
        return transformer(dom)



