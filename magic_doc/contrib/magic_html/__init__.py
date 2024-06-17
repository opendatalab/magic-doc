# -*- coding: utf-8 -*-
import json
from urllib.parse import urlparse
from magic_doc.contrib.magic_html.extractors.article_extractor import ArticleExtractor
from magic_doc.contrib.magic_html.extractors.weixin_extractor import WeixinExtractor
from magic_doc.contrib.magic_html.extractors.forum_extractor import ForumExtractor
from magic_doc.contrib.magic_html.extractors.custom_extractor import CustomExtractor


class GeneralExtractor:
    def __init__(self, config_path=""):
        if config_path:
            """
            demo rule config file json:
            {
                "www.***.com": {
                    "clean": ["//script", "//style"],
                    "title": {
                        "mode": "xpath",
                        "value": "//div[@class='media-body']/h4/text()"
                    },
                    "content": {
                        "mode": "xpath",
                        "value": "//div[@class='message break-all']"
                    }
                }
            }     
            """
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.rule = json.loads(f.read())
            except:
                pass
        else:
            self.rule = {}

    def extract(self, html="", **kwargs) -> dict:
        base_url = kwargs.get("base_url", "")
        html_type = kwargs.pop("html_type", None)
        if html_type:
            if html_type == "forum":
                return ForumExtractor().extract(html=html, **kwargs)
            elif html_type == "weixin":
                return WeixinExtractor().extract(html=html, **kwargs)
        if base_url:
            netloc = urlparse(base_url).netloc
            if netloc in self.rule:
                try:
                    new_kwargs = dict()
                    new_kwargs["rule"] = self.rule[netloc]
                    new_kwargs.update(kwargs)
                    return CustomExtractor().extract(html=html, **new_kwargs)
                except:
                    # 当自定义规则不能覆盖站点所有板块时，使用
                    return ArticleExtractor().extract(html=html, **kwargs)
            if netloc == "mp.weixin.qq.com":
                return WeixinExtractor().extract(html=html, **kwargs)
        return ArticleExtractor().extract(html=html, **kwargs)
