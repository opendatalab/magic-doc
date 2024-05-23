import json
from magic_doc.conv.base import BaseConv
from magic_html import GeneralExtractor
from loguru import logger

extractor = GeneralExtractor()


class Html(BaseConv):
    @logger.catch
    def to_md(self, html: str, **kwargs) -> str:
        """
        从HTML中提取主体区域内容
        :param html:  html文本
        :param kwargs: 可选参数
            base_url   网页地址
            html_type  网页类型(支持3种)
                1. article  文章类
                2. forum    论坛类
                3. weixin   微信文章
        :return:   {
                    "base_url": "https://example.com/",
                    "drop_list": false,
                    "html": "<div><body...",
                    "title": "",
                    "xp_num": "others"
                  }
        """
        base_url = kwargs.get("base_url", "")
        html_type = kwargs.get("html_type", None)
        data = extractor.extract(html, base_url=base_url, html_type=html_type)
        return json.dumps(data, ensure_ascii=False)