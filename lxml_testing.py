import lxml.etree as ET
import codecs

hem_fil = codecs.open("hemvag.atom.xml", 'r', 'iso-8859-1')

dom = ET.parse(hem_fil)
xslt = ET.parse('atom2rss.xsl')
transform = ET.XSLT(xslt)
newdom = transform(dom)
print(ET.tostring(newdom, pretty_print=True))