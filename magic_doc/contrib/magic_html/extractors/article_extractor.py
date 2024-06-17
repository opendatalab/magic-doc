# -*- coding:utf-8 -*-

from magic_doc.contrib.magic_html.utils import *
from magic_doc.contrib.magic_html.extractors.base_extractor import BaseExtractor
from magic_doc.contrib.magic_html.extractors.title_extractor import TitleExtractor


class ArticleExtractor(BaseExtractor):
    def __init__(self) -> None:
        super().__init__()

    def extract(self, html="", base_url="") -> dict:
        html = html.replace("&nbsp;", " ").replace("&#160;", " ")
        tree = load_html(html)
        if tree is None:
            raise ValueError

        title = TitleExtractor().process(tree)

        # base_url
        base_href = tree.xpath("//base/@href")

        if base_href and "http" in base_href[0]:
            base_url = base_href[0]

        # 标签转换, 增加数学标签处理
        format_tree = self.convert_tags(tree, base_url=base_url)

        # 删除script style等标签及其内容
        normal_tree = self.clean_tags(format_tree)

        subtree, xp_num, drop_list = self.xp_1_5(normal_tree)
        if xp_num == "others":
            subtree, drop_list = self.prune_unwanted_sections(normal_tree)
        body_html = self.get_content_html(subtree, xp_num, base_url)

        return {
            "xp_num": xp_num,
            "drop_list": drop_list,
            "html": body_html,
            "title": title,
            "base_url": base_url,
        }
