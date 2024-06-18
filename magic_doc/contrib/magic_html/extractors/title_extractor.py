# -*- coding:utf-8 -*-

from magic_doc.contrib.magic_html.utils import *
from magic_doc.contrib.magic_html.config import *


class TitleExtractor:
    def extract_by_meta(self, element: HtmlElement):
        for xpath in METAS:
            title = element.xpath(xpath)
            if title:
                return "".join(title)

    def extract_by_title(self, element: HtmlElement):
        return "".join(element.xpath("//title//text()")).strip()

    def extract_by_hs(self, element: HtmlElement):
        hs = element.xpath("//h1//text()|//h2//text()|//h3//text()")
        return hs or []

    def extract_by_h(self, element: HtmlElement):
        for xpath in ["//h1", "//h2", "//h3"]:
            children = element.xpath(xpath)
            if not children:
                continue
            child = children[0]
            texts = child.xpath("./text()")
            if texts and len(texts):
                return texts[0].strip()

    def process(self, element: HtmlElement):
        title_extracted_by_meta = self.extract_by_meta(element)
        if title_extracted_by_meta:
            return title_extracted_by_meta
        title_extracted_by_h = self.extract_by_h(element)
        title_extracted_by_hs = self.extract_by_hs(element)
        title_extracted_by_title = self.extract_by_title(element)
        title_extracted_by_hs = sorted(
            title_extracted_by_hs,
            key=lambda x: similarity2(x, title_extracted_by_title),
            reverse=True,
        )
        if title_extracted_by_hs:
            return lcs_of_2(title_extracted_by_hs[0], title_extracted_by_title)

        if title_extracted_by_title:
            return title_extracted_by_title

        return title_extracted_by_h
