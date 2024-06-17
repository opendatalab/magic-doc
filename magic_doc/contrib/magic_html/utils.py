# -*- coding:utf-8 -*-

import os
import re
from gzip import decompress

import numpy as np
from lxml import etree
from lxml.html import Element, HtmlElement, HTMLParser, fromstring, tostring
from lxml.html.clean import Cleaner
from urllib3.response import HTTPResponse
from magic_doc.contrib.magic_html.config import Unique_ID

try:
    import brotli
except ImportError:
    brotli = None

try:
    from cchardet import detect as cchardet_detect
except ImportError:
    cchardet_detect = None

from difflib import SequenceMatcher

from charset_normalizer import from_bytes

HTML_PARSER = HTMLParser(
    collect_ids=False,
    default_doctype=False,
    encoding="utf-8",
    remove_comments=True,
    remove_pis=True,
)
DOCTYPE_TAG = re.compile("^< ?! ?DOCTYPE.+?/ ?>", re.I)
UNICODE_ALIASES = {"utf-8", "utf_8"}

HTML_CLEANER = Cleaner(
    annoying_tags=False,
    comments=True,
    embedded=False,
    forms=False,
    frames=False,
    javascript=False,
    links=False,
    meta=False,
    page_structure=False,
    processing_instructions=True,
    remove_unknown_tags=False,
    safe_attrs_only=False,
    scripts=False,
    style=False,
)

color_regex = re.compile(r"\\textcolor\[.*?\]\{.*?\}")

latex_image_class_names = [
    "latexcenter",
    "latex",
    "tex",
    "latexdisplay",
    "latexblock",
    "latexblockcenter",
]


def _translator():
    import py_asciimath.translator.translator as _translator

    return _translator


def ASCIIMath2Tex(*args, **kwargs):
    return _translator().ASCIIMath2Tex(*args, **kwargs)


def MathML2Tex(*args, **kwargs):
    return _translator().MathML2Tex(*args, **kwargs)


asciimath2tex = ASCIIMath2Tex(log=False)


def lcs_of_2(a, b):
    match = SequenceMatcher(None, a, b).find_longest_match(0, len(a), 0, len(b))
    return a[match[0]: match[0] + match[2]]


def lcs_of_list(*args):
    if len(args) == 2:
        return lcs_of_2(args[0], args[1])
    first = args[0]
    remains = args[1:]
    return lcs_of_2(first, lcs_of_list(*remains))


def isutf8(data):
    try:
        data.decode("UTF-8")
    except UnicodeDecodeError:
        return False
    return True


def handle_compressed_file(filecontent):
    if isinstance(filecontent, bytes):
        if filecontent[:2] == b"\x1f\x8b":
            try:
                filecontent = decompress(filecontent)
            except (EOFError, OSError):
                pass
        elif brotli is not None:
            try:
                filecontent = brotli.decompress(filecontent)
            except brotli.error:
                pass
    return filecontent


def detect_encoding(bytesobject):
    if isutf8(bytesobject):
        return ["utf-8"]
    guesses = []
    if cchardet_detect is not None:
        cchardet_guess = cchardet_detect(bytesobject)["encoding"]
        if cchardet_guess is not None:
            guesses.append(cchardet_guess.lower())
    detection_results = from_bytes(bytesobject[:15000]) or from_bytes(bytesobject)
    if len(detection_results) > 0:
        guesses.extend([r.encoding for r in detection_results])
    return [g for g in guesses if g not in UNICODE_ALIASES]


def decode_file(filecontent):
    if isinstance(filecontent, str):
        return filecontent
    htmltext = None
    filecontent = handle_compressed_file(filecontent)
    for guessed_encoding in detect_encoding(filecontent):
        try:
            htmltext = filecontent.decode(guessed_encoding)
        except (LookupError, UnicodeDecodeError):
            htmltext = None
        else:
            break
    return htmltext or str(filecontent, encoding="utf-8", errors="replace")


def strip_faulty_doctypes(htmlstring: str, beginning: str) -> str:
    if "doctype" in beginning:
        firstline, _, rest = htmlstring.partition("\n")
        return DOCTYPE_TAG.sub("", firstline, count=1) + "\n" + rest
    return htmlstring


def is_dubious_html(beginning: str) -> bool:
    return "html" not in beginning


def fromstring_bytes(htmlobject):
    tree = None
    try:
        tree = fromstring(
            htmlobject.encode("utf8", "surrogatepass"), parser=HTML_PARSER
        )
    except Exception as err:
        pass
    return tree


def load_html(htmlobject):
    if isinstance(htmlobject, HtmlElement):
        return htmlobject
    if isinstance(htmlobject, HTTPResponse) or hasattr(htmlobject, "data"):
        htmlobject = htmlobject.data
    if not isinstance(htmlobject, (bytes, str)):
        raise TypeError("incompatible input type", type(htmlobject))
    tree = None
    htmlobject = decode_file(htmlobject)
    beginning = htmlobject[:50].lower()
    check_flag = is_dubious_html(beginning)
    htmlobject = strip_faulty_doctypes(htmlobject, beginning)
    fallback_parse = False
    try:
        tree = fromstring(htmlobject, parser=HTML_PARSER)
    except ValueError:
        tree = fromstring_bytes(htmlobject)
        fallback_parse = True
    except Exception as err:
        pass
    if (tree is None or len(tree) < 1) and not fallback_parse:
        tree = fromstring_bytes(htmlobject)
    if tree is not None and check_flag is True and len(tree) < 2:
        tree = None
    return tree


def is_empty_element(node: HtmlElement):
    return not node.getchildren() and not node.text


def iter_node(element: HtmlElement):
    yield element
    for sub_element in element:
        if isinstance(sub_element, HtmlElement):
            yield from iter_node(sub_element)


def img_div_check(tree):
    """
    如果一个div中只有一张图，且子节点数小于4则保留
    """
    if len(tree.xpath(".//img")) == 1 and len(tree.xpath(".//*")) < 4:
        return False
    else:
        return True


def text_len(s):
    s = re.sub(" +", " ", s)  # 将连续的多个空格替换为一个空格
    s = re.sub("[\n\t\r]+", "\n", s)
    english_words = s.split()
    chinese_characters = re.findall(r"[\u4e00-\u9fff]", s)
    japanese_characters = re.findall(r"[\u3040-\u309F\u30A0-\u30FF]", s)
    arabic_characters = re.findall(r"[\u0600-\u06FF]", s)
    return (
            len(english_words)
            + len(chinese_characters)
            + len(japanese_characters)
            + len(arabic_characters)
    )


def alias(element):
    if element is None:
        return ""
    tag = element.tag
    # skip nth-child
    if tag in ["html", "body"]:
        return tag
    attribs = [tag]
    for k, v in element.attrib.items():
        if k == Unique_ID:
            continue
        k, v = re.sub(r"\s*", "", k), re.sub(r"\s*", "", v)
        v = re.sub(r"-\d+", "", v)
        attribs.append(f'[{k}="{v}"]' if v else f"[{k}]")
    result = "".join(attribs)

    # 直接将当前子节点属性展示上来
    nth = ""
    for child in element.getchildren():
        if child.tag in ["dt", "dd", "li"]:
            try:
                # 子节点个数
                nth += str(len(list(child.getchildren())))
            except:
                pass
            continue
        attribs = [child.tag]
        for k, v in child.attrib.items():
            if k == Unique_ID:
                continue
            k, v = re.sub(r"\s*", "", k), re.sub(r"\s*", "", v)
            v = re.sub(r"-\d+", "", v)
            attribs.append(f"[{k}]" if v else f"[{k}]")
        nth += "".join(attribs)

    result += f":{nth}"
    return result


def similarity2(s1, s2):
    if not s1 or not s2:
        return 0
    s1_set = set(list(s1))
    s2_set = set(list(s2))
    intersection = s1_set.intersection(s2_set)
    union = s1_set.union(s2_set)
    return len(intersection) / len(union)


def similarity_with_element(element1, element2):
    alias1 = alias(element1)
    alias2 = alias(element2)
    return similarity2(alias1, alias2)


def similarity_with_siblings(element, siblings):
    scores = []
    for sibling in siblings:
        # TODO: maybe compare all children not only alias
        scores.append(similarity_with_element(element, sibling))
    if not scores:
        return 0
    # 去掉一个最低值
    min_value = min(scores)
    scores.remove(min_value)
    return np.mean(scores)


def number_of_a_char(ele, xpath=".//a//text()"):
    s = "".join(ele.xpath(xpath)).strip()
    return text_len(s)


def number_of_char(ele, xpath=".//text()"):
    s = "".join(ele.xpath(xpath)).strip()
    return text_len(s) + 1


def density_of_a_text(ele, pre=0.7):
    a_char = number_of_a_char(ele)
    t_char = number_of_char(ele)
    if a_char / t_char >= pre:
        return True
    else:
        return False


def uniquify_list(l):
    return list(dict.fromkeys(l))


def trim(string):
    """Remove unnecessary spaces within a text string"""
    try:
        return " ".join(string.split()).strip()
    except (AttributeError, TypeError):
        return None


def collect_link_info(links_xpath, favor_precision=False):
    shortelems, mylist = 0, []
    threshold = 10 if not favor_precision else 50
    for subelem in links_xpath:
        subelemtext = trim(subelem.text_content())
        if subelemtext:
            mylist.append(subelemtext)
            if len(subelemtext) < threshold:
                shortelems += 1
    lengths = sum(len(text) for text in mylist)
    return lengths, len(mylist), shortelems, mylist


def link_density_test(element, text, favor_precision=False):
    links_xpath, mylist = element.findall(".//a"), []
    if links_xpath:
        if element.tag == "p":
            if favor_precision is False:
                if element.getnext() is None:
                    limitlen, threshold = 60, 0.8
                else:
                    limitlen, threshold = 30, 0.8
            else:
                limitlen, threshold = 200, 0.8
        else:
            if element.getnext() is None:
                limitlen, threshold = 300, 0.8
            else:
                limitlen, threshold = 100, 0.8
        elemlen = len(text)
        if elemlen < limitlen:
            linklen, elemnum, shortelems, mylist = collect_link_info(
                links_xpath, favor_precision
            )
            if elemnum == 0:
                return True, mylist
            if density_of_a_text(element, 0.5):
                if linklen > threshold * elemlen or (
                        elemnum > 1 and shortelems / elemnum > 0.8
                ):
                    return True, mylist
    return False, mylist


def text_strip(text):
    return text.strip() if text else text


def wrap_math(s, display=False):
    s = re.sub(r"\s+", " ", s)
    s = color_regex.sub("", s)
    s = s.replace("$", "")
    s = s.replace("\n", " ").replace("\\n", "")
    s = s.strip()
    if len(s) == 0:
        return s
    # Don't wrap if it's already in \align
    if "align" in s:
        return s
    if display:
        return "$$" + s + "$$"
    return "$" + s + "$"


def extract_asciimath(s):
    parsed = asciimath2tex.translate(s)
    return parsed


cur_file = os.path.abspath(__file__)
xsl_path = os.path.join(os.path.dirname(cur_file), "mmltex/mmltex.xsl")

xslt = etree.parse(xsl_path)
transform = etree.XSLT(xslt)


def mml_to_latex(mml_code):
    # Remove any attibutes from the math tag
    mml_code = re.sub(r"(<math.*?>)", r"\1", mml_code)
    mml_ns = mml_code.replace(
        "<math>", '<math xmlns="http://www.w3.org/1998/Math/MathML">'
    )  # Required.

    mml_ns = mml_ns.replace("&quot;", '"')
    mml_ns = mml_ns.replace("'\\\"", '"').replace("\\\"'", '"')

    # 很多网页中标签内容就是错误
    # pattern = r"(<[^<>]*?\s)(mathbackground|mathsize|mathvariant|mathfamily|class|separators|style|id|rowalign|columnspacing|rowlines|columnlines|frame|framespacing|equalrows|equalcolumns|align|linethickness|lspace|rspace|mathcolor|rowspacing|displaystyle|style|columnalign|open|close|right|left)(?=\s|>)(?![\"'][^<>]*?>)"

    pattern = r'"([^"]+?)\''
    mml_ns = re.sub(pattern, r'"\1"', mml_ns)

    mml_dom = etree.fromstring(mml_ns)
    mmldom = transform(mml_dom)
    latex_code = str(mmldom)
    return latex_code
