from flask import request
from flask_restful import Resource
from .serialization import MagicHtmlSchema
from marshmallow import ValidationError
from magic_doc.restful_api.common.custom_response import generate_response
from magic_doc.contrib.magic_html import GeneralExtractor
from loguru import logger

extractor = GeneralExtractor()


class MagicHtmlView(Resource):
    @logger.catch
    def post(self):
        """
        网页提取
        :return:
        """
        magic_html_schema = MagicHtmlSchema()
        try:
            params = magic_html_schema.load(request.get_json())
        except ValidationError as err:
            return generate_response(code=400, msg=err.messages)
        url = params.get("pageUrl", "")
        html_type = params.get("html_type")
        html = params.get("html")
        data = extractor.extract(html, base_url=url, html_type=html_type)
        return generate_response(data=data)
