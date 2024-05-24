import json
from magic_doc.conv.base import BaseConv
from magic_html import GeneralExtractor
from magic_doc.progress.pupdator import ConvProgressUpdator
from loguru import logger

extractor = GeneralExtractor()


class Html(BaseConv):

    def __init__(self, pupdator: ConvProgressUpdator):
        super().__init__(pupdator)

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


if __name__ == '__main__':
    html_str = "<!doctype html><html><head><title>Example Domain</title><meta charset='utf-8' /><meta http-equiv='Content-type' content='text/html; charset=utf-8' /><meta name='viewport' content='width=device-width, initial-scale=1' /></head><body><div><h1>Example Domain</h1><p>This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.</p><p>This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.</p><p>This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.</p><p><a href='https://www.iana.org/domains/example'>More information...</a></p></div></body></html>"
    pupdator = ConvProgressUpdator()
    result = Html(pupdator).to_md(html=html_str)
    print(result)
