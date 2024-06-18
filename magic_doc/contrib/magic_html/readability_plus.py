# -*- coding:utf-8 -*-

from lxml.etree import tounicode
from lxml.html import document_fromstring, fragment_fromstring

from magic_doc.contrib.magic_html.utils import *


def to_int(x):
    if not x:
        return None
    x = x.strip()
    if x.endswith("px"):
        return int(x[:-2])
    if x.endswith("em"):
        return int(x[:-2]) * 12
    return int(x)


def clean(text):
    text = re.sub(r"\s{255,}", " " * 255, text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    text = re.sub(r"\t|[ \t]{2,}", " ", text)
    return text.strip()


def text_length(i):
    return len(clean(i.text_content() or ""))


bad_attrs = ["width", "height", "style", "[-a-z]*color", "background[-a-z]*", "on*"]
single_quoted = "'[^']+'"
double_quoted = '"[^"]+"'
non_space = "[^ \"'>]+"
htmlstrip = re.compile(
    "<"  # open
    "([^>]+) "  # prefix
    "(?:%s) *" % ("|".join(bad_attrs),)
    + "= *(?:%s|%s|%s)"  # undesirable attributes
    % (non_space, single_quoted, double_quoted)
    + "([^>]*)"  # value  # postfix
      ">",  # end
    re.I,
)


def clean_attributes(html):
    while htmlstrip.search(html):
        html = htmlstrip.sub("<\\1\\2>", html)
    return html


class Document:
    """Class to build a etree document out of html."""

    def __init__(
            self,
            input,
            url=None,
            min_text_length=25,
            retry_length=250,
            xpath=False,
            handle_failures="discard",
            xp_num="others",
            need_comment=False,
    ):
        self.input = input
        self.html = None
        self.encoding = None
        self.positive_keywords = None
        self.negative_keywords = None
        self.url = url
        self.min_text_length = min_text_length
        self.retry_length = retry_length
        self.xpath = xpath
        self.handle_failures = handle_failures
        self.xp_num = xp_num
        self.need_comment = need_comment
        if not need_comment:
            self.REGEXES = {
                "unlikelyCandidatesRe": re.compile(
                    r"combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter",
                    re.I,
                ),
                "okMaybeItsACandidateRe": re.compile(
                    r"and|article|body|column|main|shadow", re.I
                ),
                "positiveRe": re.compile(
                    r"article|body|content|entry|hentry|main|page|pagination|post|text|blog|story",
                    re.I,
                ),
                "negativeRe": re.compile(
                    r"combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget",
                    re.I,
                ),
                "divToPElementsRe": re.compile(
                    r"<(a|blockquote|dl|div|img|ol|p|pre|table|ul)", re.I
                ),
                "videoRe": re.compile(r"https?:\/\/(www\.)?(youtube|vimeo)\.com", re.I),
            }
        else:
            self.REGEXES = {
                "unlikelyCandidatesRe": re.compile(
                    r"combx|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter",
                    re.I,
                ),
                "okMaybeItsACandidateRe": re.compile(
                    r"and|article|body|column|main|shadow", re.I
                ),
                "positiveRe": re.compile(
                    r"article|body|content|entry|hentry|main|page|pagination|post|text|blog|story",
                    re.I,
                ),
                "negativeRe": re.compile(
                    r"combx|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget",
                    re.I,
                ),
                "divToPElementsRe": re.compile(
                    r"<(a|blockquote|dl|div|img|ol|p|pre|table|ul)", re.I
                ),
                "videoRe": re.compile(r"https?:\/\/(www\.)?(youtube|vimeo)\.com", re.I),
            }

    def _html(self, force=False):
        if force or self.html is None:
            self.html = self._parse(self.input)
            if self.xpath:
                root = self.html.getroottree()
                for i in self.html.getiterator():
                    i.attrib["x"] = root.getpath(i)
        return self.html

    def _parse(self, input: HtmlElement):
        doc = input
        base_href = self.url
        if base_href:
            try:
                doc.make_links_absolute(
                    base_href,
                    resolve_base_href=True,
                    handle_failures=self.handle_failures,
                )
            except TypeError:
                doc.make_links_absolute(
                    base_href,
                    resolve_base_href=True,
                    handle_failures=self.handle_failures,
                )
        else:
            doc.resolve_base_href(handle_failures=self.handle_failures)
        return doc

    def summary(self, html_partial=False):
        try:
            ruthless = True
            while True:
                self._html(True)
                for i in self.tags(self.html, "body"):
                    i.set("id", "readabilityplusBody")
                if ruthless and self.xp_num == "others":
                    self.remove_unlikely_candidates()
                self.transform_misused_divs_into_paragraphs()
                if self.xp_num == "others":
                    candidates = self.score_paragraphs()
                    best_candidate = self.select_best_candidate(candidates)
                else:
                    best_candidate = None
                    ruthless = False
                    candidates = {}
                if best_candidate:
                    article = self.get_article(
                        candidates, best_candidate, html_partial=html_partial
                    )
                else:
                    if ruthless:
                        ruthless = False
                        continue
                    else:
                        article = self.html.find("body")
                        if article is None:
                            article = self.html
                cleaned_article = self.sanitize(article, candidates)

                article_length = len(cleaned_article or "")
                retry_length = self.retry_length
                of_acceptable_length = article_length >= retry_length
                if ruthless and not of_acceptable_length:
                    ruthless = False
                    continue
                else:
                    return cleaned_article
        except Exception as e:
            return None

    def get_article(self, candidates, best_candidate, html_partial=False):
        sibling_score_threshold = max([10, best_candidate["content_score"] * 0.2])
        if html_partial:
            output = fragment_fromstring("<div/>")
        else:
            output = document_fromstring("<div/>")
        best_elem = best_candidate["elem"]
        parent = best_elem.getparent()
        siblings = parent.getchildren() if parent is not None else [best_elem]
        for sibling in siblings:
            append = False
            if sibling is best_elem:
                append = True
            sibling_key = sibling
            if (
                    sibling_key in candidates
                    and candidates[sibling_key]["content_score"] >= sibling_score_threshold
            ):
                append = True

            if sibling.tag == "p":
                link_density = self.get_link_density(sibling)
                node_content = sibling.text or ""
                node_length = len(node_content)

                if node_length > 80 and link_density < 0.25:
                    append = True
                elif (
                        node_length <= 80
                        and link_density == 0
                        and re.search(r"\.( |$)", node_content)
                ):
                    append = True

            if append:
                if html_partial:
                    output.append(sibling)
                else:
                    output.getchildren()[0].getchildren()[0].append(sibling)
        return output

    def select_best_candidate(self, candidates):
        if not candidates:
            return None

        sorted_candidates = sorted(
            candidates.values(), key=lambda x: x["content_score"], reverse=True
        )
        for candidate in sorted_candidates[:5]:
            elem = candidate["elem"]

        best_candidate = sorted_candidates[0]
        return best_candidate

    def get_link_density(self, elem):
        link_length = 0
        for i in elem.findall(".//a"):
            link_length += text_length(i)
        total_length = text_length(elem)
        return float(link_length) / max(total_length, 1)

    def score_paragraphs(self):
        MIN_LEN = self.min_text_length
        candidates = {}
        ordered = []
        for elem in self.tags(self._html(), "p", "pre", "td"):
            parent_node = elem.getparent()
            if parent_node is None:
                continue
            grand_parent_node = parent_node.getparent()

            inner_text = clean(elem.text_content() or "")
            inner_text_len = len(inner_text)

            if inner_text_len < MIN_LEN:
                continue

            if parent_node not in candidates:
                candidates[parent_node] = self.score_node(parent_node)
                ordered.append(parent_node)

            if grand_parent_node is not None and grand_parent_node not in candidates:
                candidates[grand_parent_node] = self.score_node(grand_parent_node)
                ordered.append(grand_parent_node)

            content_score = 1
            content_score += len(inner_text.split(","))
            content_score += len(inner_text.split("，"))
            content_score += min((inner_text_len / 100), 3)

            candidates[parent_node]["content_score"] += content_score
            if grand_parent_node is not None:
                candidates[grand_parent_node]["content_score"] += content_score / 2.0

        for elem in ordered:
            candidate = candidates[elem]
            ld = self.get_link_density(elem)
            score = candidate["content_score"]

            candidate["content_score"] *= 1 - ld

        return candidates

    def class_weight(self, e):
        weight = 0
        for feature in [e.get("class", None), e.get("id", None)]:
            if feature:
                if self.xp_num == "others":
                    if self.REGEXES["negativeRe"].search(feature):
                        weight -= 25

                    if self.REGEXES["positiveRe"].search(feature):
                        weight += 25
                else:
                    if self.REGEXES["positiveRe"].search(feature):
                        weight += 25

                if self.positive_keywords and self.positive_keywords.search(feature):
                    weight += 25

                if self.negative_keywords and self.negative_keywords.search(feature):
                    weight -= 25

        if self.positive_keywords and self.positive_keywords.match("tag-" + e.tag):
            weight += 25

        if self.negative_keywords and self.negative_keywords.match("tag-" + e.tag):
            weight -= 25

        return weight

    def score_node(self, elem):
        content_score = self.class_weight(elem)
        name = elem.tag.lower()
        if name in ["div", "article"]:
            content_score += 5
        elif name in ["pre", "td", "blockquote"]:
            content_score += 3
        elif name in ["address", "ol", "ul", "dl", "dd", "dt", "li", "form", "aside"]:
            content_score -= 3
        elif name in [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "th",
            "header",
            "footer",
            "nav",
        ]:
            content_score -= 5
        return {"content_score": content_score, "elem": elem}

    def remove_unlikely_candidates(self):
        for elem in self.html.findall(".//*"):
            s = "%s %s" % (elem.get("class", ""), elem.get("id", ""))
            if len(s) < 2:
                continue
            if (
                    self.REGEXES["unlikelyCandidatesRe"].search(s)
                    and (not self.REGEXES["okMaybeItsACandidateRe"].search(s))
                    and elem.tag not in ["html", "body"]
            ):
                elem.drop_tree()

    def transform_misused_divs_into_paragraphs(self):
        for elem in self.tags(self.html, "div"):
            if not self.REGEXES["divToPElementsRe"].search(
                    str(b"".join(map(tostring, list(elem))))
            ):
                elem.tag = "p"

        for elem in self.tags(self.html, "div"):
            if elem.text and elem.text.strip():
                p = fragment_fromstring("<p/>")
                p.text = elem.text
                elem.text = None
                elem.insert(0, p)

            for pos, child in reversed(list(enumerate(elem))):
                if child.tail and child.tail.strip():
                    p = fragment_fromstring("<p/>")
                    p.text = child.tail
                    child.tail = None
                    elem.insert(pos + 1, p)
                if child.tag == "br":
                    child.drop_tree()

    def tags(self, node, *tag_names):
        for tag_name in tag_names:
            for e in node.findall(".//%s" % tag_name):
                yield e

    def reverse_tags(self, node, *tag_names):
        for tag_name in tag_names:
            for e in reversed(node.findall(".//%s" % tag_name)):
                yield e

    def sanitize(self, node, candidates):
        MIN_LEN = self.min_text_length
        for header in self.tags(node, "h1", "h2", "h3", "h4", "h5", "h6"):
            if self.class_weight(header) < 0 or self.get_link_density(header) > 0.33:
                header.drop_tree()

        for elem in self.tags(node, "iframe"):
            if "src" in elem.attrib and self.REGEXES["videoRe"].search(
                    elem.attrib["src"]
            ):
                elem.text = "VIDEO"
            else:
                elem.drop_tree()

        allowed = {}
        # Conditionally clean <table>s, <ul>s, and <div>s
        for el in self.reverse_tags(
                node, "table", "ul", "div", "aside", "header", "footer", "section"
        ):
            if el in allowed:
                continue
            weight = self.class_weight(el)
            if el in candidates:
                content_score = candidates[el]["content_score"]
            else:
                content_score = 0
            tag = el.tag

            if weight + content_score < 0:
                el.drop_tree()
            elif el.text_content().count(",") + el.text_content().count("，") < 10:
                counts = {}
                for kind in ["p", "img", "li", "a", "embed", "input"]:
                    counts[kind] = len(el.findall(".//%s" % kind))
                counts["li"] -= 100
                counts["input"] -= len(el.findall('.//input[@type="hidden"]'))

                content_length = text_length(el)
                link_density = self.get_link_density(el)

                to_remove = False
                reason = ""

                # 修改
                if el.tag == "div" and counts["img"] >= 1:
                    continue
                if counts["p"] and counts["img"] > 1 + counts["p"] * 1.3:
                    reason = "too many images (%s)" % counts["img"]
                    # to_remove = True
                elif counts["li"] > counts["p"] and tag not in ("ol", "ul"):
                    reason = "more <li>s than <p>s"
                    # to_remove = True
                elif counts["input"] > (counts["p"] / 3):
                    reason = "less than 3x <p>s than <input>s"
                    to_remove = True
                elif content_length < MIN_LEN and counts["img"] == 0:
                    reason = (
                            "too short content length %s without a single image"
                            % content_length
                    )
                    to_remove = True
                elif content_length < MIN_LEN and counts["img"] > 2:
                    reason = (
                            "too short content length %s and too many images"
                            % content_length
                    )
                    to_remove = True
                elif weight < 25 and link_density > 0.2:
                    if tag in ["div", "ul", "table"]:
                        ptest = el.xpath(".//text()[not(ancestor::a)]")
                        ptest_len = text_len("".join(ptest))
                        if ptest_len >= MIN_LEN and link_density <= 0.3:
                            continue
                    reason = "too many links %.3f for its weight %s" % (
                        link_density,
                        weight,
                    )
                    to_remove = True
                elif weight >= 25 and link_density > 0.5:
                    reason = "too many links %.3f for its weight %s" % (
                        link_density,
                        weight,
                    )
                    to_remove = True
                elif (counts["embed"] == 1 and content_length < 75) or counts[
                    "embed"
                ] > 1:
                    reason = (
                        "<embed>s with too short content length, or too many <embed>s"
                    )
                    to_remove = True
                elif not content_length:
                    reason = "no content"
                    to_remove = True

                    i, j = 0, 0
                    x = 1
                    siblings = []
                    for sib in el.itersiblings():
                        sib_content_length = text_length(sib)
                        if sib_content_length:
                            i = +1
                            siblings.append(sib_content_length)
                            if i == x:
                                break
                    for sib in el.itersiblings(preceding=True):
                        sib_content_length = text_length(sib)
                        if sib_content_length:
                            j = +1
                            siblings.append(sib_content_length)
                            if j == x:
                                break
                    if siblings and sum(siblings) > 1000:
                        to_remove = False
                        for desnode in self.tags(el, "table", "ul", "div", "section"):
                            allowed[desnode] = True

                if to_remove:
                    el.drop_tree()
                else:
                    pass

        self.html = node
        return self.get_clean_html()

    def get_clean_html(self):
        return clean_attributes(tounicode(self.html, method="html"))
