# -*- coding:utf-8 -*-

import html
from collections import defaultdict
from copy import deepcopy
from urllib.parse import unquote, urljoin
from lxml.etree import Comment, strip_elements
from magic_doc.contrib.magic_html.config import *
from magic_doc.contrib.magic_html.readability_plus import Document as DocumentPlus
from magic_doc.contrib.magic_html.utils import *


class BaseExtractor:
    def __init__(self):
        self.drop_ids = []
        self.need_comment = False

    def xp_1_5(self, tree: HtmlElement):
        drop_list = False
        xp_num = "others"
        result_body = Element("body")

        for idx, expr in enumerate(BODY_XPATH):
            try:
                subtree = tree.xpath(expr)[0]
                xp_num = str(idx + 1)
            except IndexError:
                continue

            subtree, drop_list = self.prune_unwanted_sections(subtree)

            if len(subtree) == 0:
                xp_num = "others"
                continue

            ptest = subtree.xpath(".//text()[not(ancestor::a)]")
            ptest_len = text_len("".join(ptest))
            all_text_len = text_len(
                "".join(tree.xpath("//p//text()[not(ancestor::a)]"))
            )
            if drop_list:
                if ptest_len <= 50:
                    if all_text_len > 100:
                        xp_num = "others"
                    continue
            else:
                if ptest_len <= 20:
                    if all_text_len > 100:
                        xp_num = "others"
                    continue
            result_body.append(subtree)
            return result_body, xp_num, drop_list

        return result_body, xp_num, drop_list

    def get_content_html(self, cleaned_tree_backup, xp_num="others", base_url=""):
        # readability_plus
        doc = DocumentPlus(
            cleaned_tree_backup,
            url=base_url,
            xp_num=xp_num,
            need_comment=self.need_comment,
        )
        body = doc.summary(html_partial=True)

        return body

    def prune_unwanted_nodes(self, tree, nodelist, with_backup=False):
        if with_backup is True:
            old_len = len(tree.text_content())
            backup = deepcopy(tree)
        for expr in nodelist:
            for subtree in tree.xpath(expr):

                # DISCARD_IMAGE_ELEMENTS 需要特殊判断
                if '"caption"' in expr and subtree.xpath(".//img"):
                    continue
                # 有些出现hidden
                if "hidden" in expr:
                    try:
                        if re.findall(
                                "overflow-x:\s*hidden", subtree.attrib["style"]
                        ) or re.findall(
                            "overflow-y:\s*hidden", subtree.attrib["style"]
                        ):
                            continue
                        if re.findall(
                                "overflow:\s*hidden", subtree.attrib["style"]
                        ) and re.findall("height:", subtree.attrib["style"]):
                            height_px = re.findall(
                                "height:\s*(\d+)", subtree.attrib["style"]
                            )[0]
                            if int(height_px) >= 800:
                                continue
                    except:
                        pass
                self.remove_node(subtree)
        if with_backup is False:
            return tree
        # else:
        new_len = len(tree.text_content())
        if new_len > old_len / 7:
            return tree
        return backup

    def prune_html(self, tree):
        """Delete selected empty elements"""
        for element in tree.xpath(".//*[not(node())]"):
            if element.tag in CUT_EMPTY_ELEMS:
                self.remove_node(element)
        return tree

    def remove_node(self, node: HtmlElement):
        parent = node.getparent()
        if text_strip(node.tail):
            previous = node.getprevious()
            if previous is None:
                if parent is not None:
                    if text_strip(parent.text):
                        parent.text = "".join([parent.text, node.tail])
                    else:
                        parent.text = node.tail
            else:
                if text_strip(previous.tail):
                    previous.tail = "".join([previous.tail, node.tail])
                else:
                    previous.tail = node.tail

        if parent is not None:
            idx = node.attrib.get(Unique_ID, "")
            parent.remove(node)
            if idx:
                self.drop_ids.append(int(idx))

    def clean_tags(self, tree):
        strip_elements(tree, Comment)

        xp_lists = []
        if not self.need_comment:
            xp_lists.append(REMOVE_COMMENTS_XPATH)
        xp_lists.append(CONTENT_EXTRACTOR_NOISE_XPATHS)
        for xp_list in xp_lists:
            tree = self.prune_unwanted_nodes(tree, xp_list)

        cleaning_list, stripping_list = (
            MANUALLY_CLEANED.copy(),
            MANUALLY_STRIPPED.copy(),
        )

        for elem in tree.xpath(".//figure[descendant::table]"):
            elem.tag = "div"

        for expression in cleaning_list + ["form"]:
            for element in tree.getiterator(expression):
                # 针对form 标签特殊处理
                if element.tag == "form":
                    ptest = element.xpath(".//text()[not(ancestor::a)]")
                    if text_len("".join(ptest)) <= 60:  # 50
                        self.remove_node(element)
                else:
                    self.remove_node(element)

        HTML_CLEANER.kill_tags, HTML_CLEANER.remove_tags = cleaning_list, stripping_list
        cleaned_tree = HTML_CLEANER.clean_html(self.prune_html(tree))

        return cleaned_tree

    def generate_unique_id(self, element):
        idx = 0
        for node in iter_node(element):
            l_tag = node.tag.lower()
            if l_tag not in ["html", "body"]:
                node.attrib[Unique_ID] = str(idx)
                idx += 1

    def clean_unique_id(self, raw_element, content_html):
        ids = re.findall(f' {Unique_ID}="(\d+)"', content_html)
        self.drop_ids = list(set(self.drop_ids))
        self.drop_ids.sort()
        skip_ids = [-1]
        for x in ids:
            if int(x) > int(skip_ids[-1]):
                skip_ids.append(int(x))
                drop_node = raw_element.xpath(
                    f"//*[@{Unique_ID}='{x}']"
                )
                if drop_node:
                    new_div = Element("div")
                    for j in self.drop_ids:
                        if int(j) > int(skip_ids[-1]):
                            append_element = drop_node[0].xpath(
                                f".//*[@{Unique_ID}='{j}']"
                            )
                            if append_element:
                                skip_ids.append(j)
                                if len(append_element[0]) > 0:
                                    skip_ids.extend(
                                        [
                                            int(pjid)
                                            for pjid in append_element[0].xpath(
                                            f".//*/@{Unique_ID}"
                                        )
                                        ]
                                    )
                                append_element[0].tail = None
                                new_div.append(append_element[0])

                    try:
                        drop_node[0].addnext(new_div)
                        parent = drop_node[0].getparent()
                        if parent is not None:
                            parent.remove(drop_node[0])
                    except:
                        pass

        content_html = re.sub(f' {Unique_ID}="\d+"', "", content_html)

        drop_html = re.sub(
            f' {Unique_ID}="\d+"',
            "",
            tostring(raw_element, encoding=str),
        )
        return content_html, drop_html

    def math_latex_processing(self, node):
        # 1. 文本中有\\begin{align} 或 \\begin{equation}
        if node.tag not in ["script", "style"] and text_strip(node.text):
            regex = r"\\begin{align}(.*?)\\end{align}"
            text = node.text
            matches = re.findall(regex, text, re.DOTALL)
            if matches:
                node.text = text.replace("\\begin{align}", "").replace(
                    "\\end{align}", ""
                )

        if node.tag not in ["script", "style"] and text_strip(node.text):
            regex = r"\\begin{equation}(.*?)\\end{equation}"
            text = node.text
            matches = re.findall(regex, text, re.DOTALL)
            for match in matches:
                match = match.replace("\\begin{equation}", "")
                match = match.replace("\\end{equation}", "")
                wrapped_text = wrap_math(match, display=True)
                text = text.replace(match, wrapped_text)
            if matches:
                # Remove the \begin{equation} and \end{equation} tags
                text = text.replace("\\begin{equation}", "").replace(
                    "\\end{equation}", ""
                )
                node.text = text

        if node.tag not in ["script", "style"] and text_strip(node.tail):
            regex = r"\\begin{align}(.*?)\\end{align}"
            text = node.tail
            matches = re.findall(regex, text, re.DOTALL)
            if matches:
                node.tail = text.replace("\\begin{align}", "").replace(
                    "\\end{align}", ""
                )

        if node.tag not in ["script", "style"] and text_strip(node.tail):
            regex = r"\\begin{equation}(.*?)\\end{equation}"
            text = node.tail
            matches = re.findall(regex, text, re.DOTALL)
            for match in matches:
                match = match.replace("\\begin{equation}", "")
                match = match.replace("\\end{equation}", "")
                wrapped_text = wrap_math(match, display=True)
                text = text.replace(match, wrapped_text)
            if matches:
                # Remove the \begin{equation} and \end{equation} tags
                text = text.replace("\\begin{equation}", "").replace(
                    "\\end{equation}", ""
                )
                node.tail = text

        node_class = node.get("class")

        parent = node.getparent()

        # 2. class 为 texerror 的标签
        # Find the text between {} (maximum length) and replace the texerror with that text

        # 3. img中的latex
        if node.tag == "img":
            if node_class:
                class_list = node_class.split(" ")
                if any(
                        [img_class in class_list for img_class in latex_image_class_names]
                ):
                    alt = node.get("alt")
                    if text_strip(alt):
                        new_span = Element("span")
                        wrapped_alt = wrap_math(alt)
                        new_span.text = wrapped_alt
                        node.addprevious(new_span)
            src = node.get("src")
            if src:
                if "codecogs.com" in src:
                    try:
                        latex = src.split("?")[1:]
                        latex = "?".join(
                            latex
                        )  # In case there are multiple ? in the latex
                        latex = unquote(latex)
                        new_span = Element("span")
                        wrapped_latex = wrap_math(latex)
                        new_span.text = wrapped_latex
                        node.addprevious(new_span)
                    except:
                        pass
                if "latex.php" in src:
                    try:
                        # they usually have "alt='-i u_t + &#92;Delta u = |u|^2 u'"
                        alt = node.get("alt")
                        if text_strip(alt):
                            # Unescape the latex
                            alt = unquote(alt)
                            # Get the latex
                            wrapped_alt = wrap_math(alt)
                            new_span = Element("span")
                            new_span.text = wrapped_alt
                            node.addprevious(new_span)
                    except:
                        pass
                if "/images/math/codecogs" in src:
                    try:
                        # they usually have "alt='-i u_t + &#92;Delta u = |u|^2 u'"
                        alt = node.get("alt")
                        if text_strip(alt):
                            # Unescape the latex
                            alt = unquote(alt)
                            # Get the latex
                            wrapped_alt = wrap_math(alt)
                            new_span = Element("span")
                            new_span.text = wrapped_alt
                            node.addprevious(new_span)
                    except:
                        pass
                if "mimetex.cgi" in src:
                    try:
                        latex = src.split("?")[1:]
                        latex = "?".join(
                            latex
                        )  # In case there are multiple ? in the latex
                        latex = unquote(latex)
                        new_span = Element("span")
                        wrapped_latex = wrap_math(latex)
                        new_span.text = wrapped_latex
                        node.addprevious(new_span)
                    except:
                        pass
                if "mathtex.cgi" in src:
                    try:
                        latex = src.split("?")[1:]
                        latex = "?".join(
                            latex
                        )  # In case there are multiple ? in the latex
                        latex = unquote(latex)
                        new_span = Element("span")
                        wrapped_latex = wrap_math(latex)
                        new_span.text = wrapped_latex
                        node.addprevious(new_span)
                    except:
                        pass
            if node_class:
                if "x-ck12" in node_class:
                    try:
                        latex = node.get("alt")
                        if text_strip(latex):
                            latex = unquote(latex)
                            new_span = Element("span")
                            wrapped_latex = wrap_math(latex)
                            new_span.text = wrapped_latex
                            node.addprevious(new_span)
                    except:
                        pass

        # 4. class 为 math-container
        if node_class == "math-container":
            try:
                text = node.text
                if text_strip(text):
                    new_span = Element("span")
                    wrapped_math = wrap_math(text, display=True)
                    new_span.text = wrapped_math
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
            except:
                pass

        # 5. class 为 wp-katex-eq
        if node_class == "wp-katex-eq":
            try:
                text = node.text
                if text_strip(text):
                    new_span = Element("span")
                    display_attr = node.get("data-display")
                    if display_attr is not None:
                        display = display_attr == "true"
                    else:
                        display = False
                    wrapped_math = wrap_math(text, display=display)
                    new_span.text = wrapped_math
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
            except:
                pass

        # 6. script[type="math/tex"]
        if node.tag == "script" and node.get("type") == "math/tex":
            try:
                text = node.text
                if text_strip(text):
                    new_span = Element("span")
                    wrapped_text = wrap_math(text)
                    new_span.text = wrapped_text
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
            except:
                pass

        # 7. script[type="math/asciimath"]
        if node.tag == "script" and node.get("type") == "math/asciimath":
            try:
                text = node.text
                if text_strip(text):
                    new_span = Element("span")
                    wrapped_asciimath = wrap_math(extract_asciimath(text))
                    new_span.text = wrapped_asciimath
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
            except:
                # Delete this script tag
                self.remove_node(node)

        # 8. class tex
        if node_class == "tex":
            try:
                # Check if they have data-expr attr
                expr = node.get("data-expr")
                if text_strip(expr):
                    # Replace with a span
                    new_span = Element("span")
                    wrapped_expr = wrap_math(expr)
                    new_span.text = wrapped_expr
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
            except:
                pass

        # 9. span.katex
        if node.tag == "span" and node_class == "katex":
            # Find any spans with class "katex-html" and remove them
            katex_html_spans = node.xpath('.//span[@class="katex-html"]')
            for katex_html_span in katex_html_spans:
                self.remove_node(katex_html_span)

        # 10. Remove any .MathJax_Preview spans
        if node.tag == "span" and node_class == "MathJax_Preview":
            self.remove_node(node)

        if node.tag == "span" and node_class and "x-ck12-mathEditor" in node_class:
            try:
                expr = node.get("data-tex")
                if text_strip(expr):
                    expr = unquote(expr).replace("\&quot;", "").replace("&quot;", "")
                    # Replace with a span
                    new_span = Element("span")
                    wrapped_expr = wrap_math(expr)
                    new_span.text = wrapped_expr
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
            except:
                pass

        # 11. all math tags
        if node.tag == "math":
            annotation_tags = node.xpath('.//annotation[@encoding="application/x-tex"]')
            if len(annotation_tags) > 0:
                annotation_tag = annotation_tags[0]
                text = annotation_tag.text
                if text_strip(text):
                    new_span = Element("span")
                    wrapped_text = wrap_math(text)
                    new_span.text = wrapped_text
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
                    style_value = parent.get("style")
                    if style_value:
                        normalized_style_value = (
                            style_value.lower()
                            .strip()
                            .replace(" ", "")
                            .replace(";", "")
                        )
                        if "display:none" in normalized_style_value:
                            parent.style = ""
            elif text_strip(node.get("alttext")):
                # Get the alttext attribute
                alttext = node.get("alttext")
                if text_strip(alttext):
                    new_span = Element("span")
                    wrapped_alttext = wrap_math(alttext)
                    new_span.text = wrapped_alttext
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
            else:
                try:
                    # Try translating to LaTeX
                    tmp_node = deepcopy(node)
                    tmp_node.tail = None
                    mathml = tostring(tmp_node, encoding=str)
                    # If this includes xmlns:mml, then we need to replace all
                    # instances of mml: with nothing
                    if "xmlns:mml" in mathml:
                        mathml = mathml.replace("mml:", "")
                        # replace xmlns:mml="..." with nothing
                        mathml = re.sub(r'xmlns:mml=".*?"', "", mathml)
                    # if 'xmlns=' in mathml:
                    #     mathml = re.sub(r"xmlns='.*?'", '', mathml)
                    latex = mml_to_latex(mathml)
                    # Make a new span tag
                    new_span = Element("span")
                    # Set the html of the new span tag to the text
                    wrapped_latex = wrap_math(latex)
                    new_span.text = wrapped_latex
                    # Then, we need to replace the math tag with the new span tag
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
                except:

                    self.remove_node(node)

        if node.tag == "mathjax":
            try:
                # Get the inner text of the mathjax tag
                text = node.text
                if text_strip(text):
                    text = html.unescape(text)
                    # Use regex to find text wrapped in hashes
                    matches = re.findall(r"#(.+?)#", text)
                    # For each match, replace the match with the LaTeX
                    for match in matches:
                        try:
                            latex = extract_asciimath(match)
                            # Replace the match with the LaTeX
                            text = text.replace(f"#{match}#", latex)
                        except:

                            pass
                    # Create a new span tag
                    new_span = Element("span")
                    # Set the html of the new span tag to the text
                    new_span.text = text
                    # Then, we need to replace the mathjax tag with the new span tag
                    if parent is not None:
                        if text_strip(node.tail):
                            new_span.tail = node.tail
                        parent.replace(node, new_span)
            except:
                pass

    def convert_tags(self, element, base_url=""):
        USELESS_ATTR_LIST = USELESS_ATTR
        if not self.need_comment:
            USELESS_ATTR_LIST = USELESS_ATTR_LIST + ["comment"]
        for node in iter_node(element):

            # 增加数学标签转换
            self.math_latex_processing(node)

            if "data-src" in node.attrib and "src" not in node.attrib:
                node.attrib["src"] = node.attrib["data-src"]
            if "src" in node.attrib and node.attrib["src"] and base_url:
                src_url = node.attrib["src"]
                absolute_url = urljoin(base_url, src_url)
                node.attrib["src"] = absolute_url

            if node.tag.lower() == "div" and not node.getchildren():
                node.tag = "p"

            class_name = node.get("class")
            if class_name:
                if class_name.lower() in USELESS_ATTR_LIST:
                    self.remove_node(node)

        return element

    def delete_by_link_density(
            self, subtree, tagname, backtracking=False, favor_precision=False
    ):
        need_del_par = []
        skip_par = []
        drop_list = False
        for descendant in subtree.iter(tagname):
            pparent = descendant.getparent()
            if pparent in need_del_par or pparent in skip_par:
                continue
            siblings = descendant.xpath(f"following-sibling::{tagname}")
            nn = [descendant]
            nn.extend(siblings)
            txt_max_num = 0
            if len(siblings) + 1 >= 4:
                pass
            else:
                txt_max_dict = {
                    "read": 0,
                    "more": 0,
                    "...": 0,
                    "阅读": 0,
                    "更多": 0,
                    "详细": 0,
                    "detail": 0,
                    "article": 0,
                    "blog": 0,
                    "news": 0,
                }
                if tagname == "div" or tagname == "article" or tagname == "section":
                    for j in nn:
                        txt = "".join(j.xpath(".//text()")).strip()
                        for x in [
                            "read",
                            "more",
                            "...",
                            "阅读",
                            "更多",
                            "详细",
                            "detail",
                            "article",
                            "blog",
                            "news",
                        ]:
                            if txt.lower().endswith(x):
                                txt_max_dict[x] += 1
                        txt_num = max(txt_max_dict.values())
                        if txt_max_num < txt_num:
                            txt_max_num = txt_num
                        if txt_max_num >= 3:
                            break
                if txt_max_num >= 3:
                    pass
                else:
                    continue
            skip_par.append(pparent)
            a_num = 0
            for j in siblings:
                if j.xpath(".//a"):
                    if tagname == "p":
                        if density_of_a_text(j, pre=0.8):
                            a_num += 1
                    elif tagname in ["div", "section", "article"]:
                        if density_of_a_text(j, pre=0.2):
                            a_num += 1
                    else:
                        if self.need_comment:
                            # 增加判断是否包含评论 再决定是否删除
                            break_flg = False
                            for c_xpath in Forum_XPATH[:-1]:
                                if j.xpath(c_xpath.replace(".//*", "self::*")):
                                    break_flg = True
                                    break
                            if break_flg:
                                continue
                        if tagname == "li":
                            if text_len("".join(j.xpath(".//text()[not(ancestor::a)]"))) > 50:
                                continue
                        a_num += 1

            if a_num < len(siblings):
                if a_num >= 15 and (
                        tagname == "div" or tagname == "article" or tagname == "section"
                ):
                    pass
                else:
                    continue

            similarity_with_siblings_nums = similarity_with_siblings(
                descendant, siblings
            )
            if tagname == "article" or tagname == "item":  # or tagname == "section"
                similarity_with_siblings_nums = similarity_with_siblings_nums * 1.5
            # 列表有个很特殊的地方 另一种情况就是 descendant和siblings 都包含title/h1 | h2 标签
            if tagname == "div" or tagname == "article" or tagname == "section":
                title_max_num = 0
                for ll in [".//head[@rend='h2']", ".//head[@rend='h1']", "./article"]:
                    title_num = 0
                    for jj in nn:
                        if jj.xpath(ll):
                            title_num += 1
                    if title_max_num < title_num:
                        title_max_num = title_num
                if title_max_num >= 4:
                    similarity_with_siblings_nums = similarity_with_siblings_nums * 1.5

            if txt_max_num >= 3:
                pass
            elif similarity_with_siblings_nums < 0.84:
                if len(siblings) >= 15 and (
                        tagname == "div" or tagname == "article" or tagname == "section"
                ):
                    pass
                else:
                    continue
            # 父div中包含多同级div 且div class post-时，删除其余节点，保留第一篇文章
            class_attr = descendant.get("class") if descendant.get("class") else ""
            if (
                    re.findall("post-", class_attr, re.I)
                    or re.findall("-post", class_attr, re.I)
                    or re.findall("blog|aricle", class_attr, re.I)
            ):
                drop_list = True
                sk_flg = True
                for dl in siblings:
                    if (
                            text_len("".join(descendant.xpath(".//text()"))) * 2
                            < text_len("".join(dl.xpath(".//text()")))
                            and sk_flg
                    ):
                        self.remove_node(descendant)
                        sk_flg = False
                    else:
                        self.remove_node(dl)
            else:
                need_del_par.append(descendant)
                need_del_par.extend(siblings)
        for node in need_del_par:
            drop_list = True
            try:
                self.remove_node(node)
            except Exception as e:
                pass

        myelems, deletions = defaultdict(list), []

        if tagname == "div":
            for elem in subtree.iter(tagname):
                if density_of_a_text(elem, pre=0.8) and img_div_check(elem):
                    deletions.append(elem)

        for elem in subtree.iter(tagname):
            elemtext = trim(elem.text_content())
            result, templist = link_density_test(elem, elemtext, favor_precision)
            if result is True and img_div_check(elem):
                deletions.append(elem)
            elif backtracking is True and len(templist) > 0:  # if?
                myelems[elemtext].append(elem)
        if backtracking is True:
            if favor_precision is False:
                threshold = 100
            else:
                threshold = 200
            for text, elem in myelems.items():
                if 0 < len(text) < threshold and len(elem) >= 3:
                    deletions.extend(elem)

        for elem in uniquify_list(deletions):
            try:
                if self.need_comment:
                    # 增加判断是否包含评论 再决定是否删除
                    break_flg = False
                    for c_xpath in Forum_XPATH[:-1]:
                        if elem.xpath(c_xpath):
                            break_flg = True
                            break
                    if break_flg:
                        continue
                self.remove_node(elem)
            except AttributeError:
                pass
        return subtree, drop_list

    def prune_unwanted_sections(self, tree):
        tmp_OVERALL_DISCARD_XPATH = OVERALL_DISCARD_XPATH
        if self.need_comment:
            tmp_OVERALL_DISCARD_XPATH = tmp_OVERALL_DISCARD_XPATH[:-1]
        tree = self.prune_unwanted_nodes(
            tree, tmp_OVERALL_DISCARD_XPATH, with_backup=True
        )
        for xp_list in [
            PAYWALL_DISCARD_XPATH,
            TEASER_DISCARD_XPATH,
            DISCARD_IMAGE_ELEMENTS,
        ]:
            tree = self.prune_unwanted_nodes(tree, xp_list)
        # remove elements by link density
        tree, drop_list_1 = self.delete_by_link_density(
            tree, "div", backtracking=True, favor_precision=False
        )
        tree, drop_list_1_1 = self.delete_by_link_density(
            tree, "article", backtracking=False, favor_precision=False
        )
        tree, drop_list_1_2 = self.delete_by_link_density(
            tree, "section", backtracking=False, favor_precision=False
        )
        tree, drop_list_2_1 = self.delete_by_link_density(
            tree, "ul", backtracking=False, favor_precision=False
        )
        tree, drop_list_2_2 = self.delete_by_link_density(
            tree, "li", backtracking=False, favor_precision=False
        )
        tree, drop_list_3_1 = self.delete_by_link_density(
            tree, "dl", backtracking=False, favor_precision=False
        )
        tree, drop_list_3_3 = self.delete_by_link_density(
            tree, "dt", backtracking=False, favor_precision=False
        )
        tree, drop_list_3_2 = self.delete_by_link_density(
            tree, "dd", backtracking=False, favor_precision=False
        )
        tree, drop_list_3 = self.delete_by_link_density(
            tree, "p", backtracking=False, favor_precision=False
        )

        return (
            tree,
            drop_list_1
            or drop_list_2_1
            or drop_list_2_2
            or drop_list_3
            or drop_list_1_1
            or drop_list_1_2
            or drop_list_3_1
            or drop_list_3_2
            or drop_list_3_3,
        )
