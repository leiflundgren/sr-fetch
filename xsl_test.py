from lxml import etree

with open( 'atom2rss.xsl', 'r' ) as xslt, open( 'hemvag.rss-out.xml', 'a+' ) as result, open( 'hemvag.atom.xml', 'r' ) as xml:
    s_xml = etree.parse(xml.read())
    s_xslt = etree.parse(xslt.read())
    transform = etree.XSLT(s_xslt)
    out = transform(s_xml)
    result.write(out)
    print(out.tostring())

