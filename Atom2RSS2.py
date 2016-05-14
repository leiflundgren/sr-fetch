import lxml.etree as ET
from common import trace
from common import pretty

 
class Atom2RSS2(object):
    """Converts an atom feed to an rss. Manually using xpaths"""

    def __init__(self):
        self.ns = { 'itunes':"http://www.itunes.com/dtds/podcast-1.0.dtd", 'atom':"http://www.w3.org/2005/Atom" }

    def transform(self, atom_thing):
        if isinstance(atom_thing, basestring):
            atom_thing = ET.parse(atom_thing)

        trace(8, 'transforming atom_thing: ', str(type(atom_thing)))
        
        rss = ET.Element('rss')


if __name__ == '__main__':
    atom = ET.parse('p1hist.atom.xml')
    rss = Atom2RSS(False).transform(atom)
    print ET.tostring(rss, pretty_print=True)
    pass
