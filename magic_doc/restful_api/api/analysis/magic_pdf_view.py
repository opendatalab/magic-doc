from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from .serialization import MagicPdfSchema
from magic_doc.restful_api.common.custom_response import generate_response
from loguru import logger


class MagicPdfView(Resource):
    @logger.catch
    def post(self):
        magic_pdf_schema = MagicPdfSchema()
        try:
            params = magic_pdf_schema.load(request.get_json())
        except ValidationError as err:
            return generate_response(code=400, msg=err.messages)
        pdf_url = params.get('pageUrl')
        # todo
        # pdf解析
        return generate_response(markDownUrl=pdf_url)
