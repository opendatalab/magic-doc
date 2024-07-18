from flask import Blueprint
from .magic_pdf_view import *
from ..extentions import Api

analysis_blue = Blueprint('analysis', __name__, url_prefix='/analysis')

api = Api(analysis_blue)
api.add_resource(MagicPdfView, '/pdf')