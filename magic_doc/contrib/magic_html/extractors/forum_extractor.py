# -*- coding:utf-8 -*-
import re

from magic_doc.contrib.magic_html.config import Forum_XPATH, Unique_ID
from magic_doc.contrib.magic_html.utils import *
from magic_doc.contrib.magic_html.extractors.base_extractor import BaseExtractor
from magic_doc.contrib.magic_html.extractors.title_extractor import TitleExtractor


class ForumExtractor(BaseExtractor):
    def __init__(self) -> None:
        super().__init__()

    def extract(self, html="", base_url="") -> dict:
        self.need_comment = True
        html = html.replace("&nbsp;", " ").replace("&#160;", " ")
        tree = load_html(html)
        if tree is None:
            raise ValueError

        # 获取title
        title = TitleExtractor().process(tree)

        # base_url
        base_href = tree.xpath("//base/@href")

        if base_href and "http" in base_href[0]:
            base_url = base_href[0]
        self.generate_unique_id(tree)

        format_tree = self.convert_tags(tree, base_url=base_url)

        normal_tree = self.clean_tags(format_tree)

        subtree, xp_num, drop_list = self.xp_1_5(normal_tree)
        if xp_num == "others":
            subtree, drop_list = self.prune_unwanted_sections(normal_tree)
        body_html = self.get_content_html(subtree, xp_num, base_url)

        # 论坛等独有
        body_html_tree = fromstring(body_html)
        try:
            body_tree = body_html_tree.body
        except:
            body_tree = Element("body")
            body_tree.extend(body_html_tree)
        main_ids = body_tree.xpath(f".//@{Unique_ID}")

        for main_id in main_ids:
            main_tree = normal_tree.xpath(
                f".//*[@{Unique_ID}={main_id}]"
            )
            if main_tree:
                self.remove_node(main_tree[0])
        if not main_ids:
            main_ids = [-1]

        if xp_num != "others":
            normal_tree, _ = self.prune_unwanted_sections(normal_tree)
        for c_xpath in Forum_XPATH:
            while normal_tree.xpath(c_xpath):
                x = normal_tree.xpath(c_xpath)[0]
                self.remove_node(x)
                if "'post-'" in c_xpath:
                    if not (re.findall('post-\d+', x.attrib.get("id", "").lower()) or re.findall('post_\d+',
                                                                                                 x.attrib.get("id",
                                                                                                              "").lower())):
                        continue
                if (
                        "header" in x.attrib.get("class", "").lower()
                        or "header" in x.attrib.get("id", "").lower()
                ):
                    continue
                try:
                    if int(x.attrib.get(Unique_ID, "0")) > int(
                            main_ids[-1]
                    ):
                        body_tree.append(x)
                    else:
                        prefix_div = Element("div")
                        suffix_div = Element("div")
                        need_prefix = False
                        need_suffix = False
                        while x.xpath(
                                f".//*[number(@{Unique_ID}) > {int(main_ids[-1])}]"
                        ):
                            tmp_x = x.xpath(
                                f".//*[number(@{Unique_ID}) > {int(main_ids[-1])}]"
                            )[0]
                            self.remove_node(tmp_x)
                            suffix_div.append(tmp_x)
                            need_suffix = True
                        while x.xpath(
                                f".//*[number(@{Unique_ID}) < {int(main_ids[-1])}]"
                        ):
                            tmp_x = x.xpath(
                                f".//*[number(@{Unique_ID}) < {int(main_ids[-1])}]"
                            )[0]
                            self.remove_node(tmp_x)
                            prefix_div.append(tmp_x)
                            need_prefix = True
                        if need_prefix:
                            body_tree.insert(0, prefix_div)
                        if need_suffix:
                            body_tree.append(suffix_div)

                except:
                    pass

        body_html = re.sub(
            f' {Unique_ID}="\d+"',
            "",
            tostring(body_tree, encoding=str),
        )

        return {
            "xp_num": xp_num,
            "drop_list": drop_list,
            "html": body_html,
            "title": title,
            "base_url": base_url
        }
