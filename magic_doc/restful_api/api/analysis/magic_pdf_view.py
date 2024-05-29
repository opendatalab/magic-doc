from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from pathlib import Path
from magic_doc.pdf_transform import DocConverter
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
        # pdf解析
        file_name = str(Path(pdf_url).stem)
        pf_path = f"/tmp/{file_name}.txt"
        docconv = DocConverter(None)
        result = docconv.convert_to_mid_result(pdf_url, pf_path, 60)
        return generate_response(data=result, markDownUrl=pdf_url)
