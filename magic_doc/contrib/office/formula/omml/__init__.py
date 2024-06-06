import os
import string

from lxml import etree as ET

from ..mml import mml2tex


_namespaces = {
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "cx": "http://schemas.microsoft.com/office/drawing/2014/chartex",
    "cx1": "http://schemas.microsoft.com/office/drawing/2015/9/8/chartex",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "o": "urn:schemas-microsoft-com:office:office",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v": "urn:schemas-microsoft-com:vml",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
}
_xmlns_str = " ".join(
    'xmlns:{}="{}"'.format(key, value) for key, value in _namespaces.items()
)

_template = string.Template(
    """<?xml version="1.0" standalone="yes"?>
<w:document mc:Ignorable="w14 w15 w16se wp14" {}>
    $omml_xml
</w:document>""".format(
        _xmlns_str
    )
)


transform = None

_xslt_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "OMML2MML.XSL"
)


def omml2mml(omml_xml):
    xml_content = _template.safe_substitute(omml_xml=omml_xml)
    tree = ET.fromstring(xml_content)
    global transform
    if not transform:
        transform = ET.XSLT(ET.parse(_xslt_filename))
    return str(transform(tree))


def omml2tex(omml_xml):
    mml_xml = omml2mml(omml_xml)
    return mml2tex(mml_xml)
