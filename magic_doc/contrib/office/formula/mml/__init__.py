import os

from lxml import etree as ET

transform = None

_xslt_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "xsl/mmltex.xsl"
)


def mml2tex(mml_xml):
    tree = ET.fromstring(mml_xml)
    global transform
    if not transform:
        transform = ET.XSLT(ET.parse(_xslt_filename))
    return str(transform(tree))
