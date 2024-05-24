from io import BytesIO

from werkzeug.datastructures import FileStorage

from magic_doc.contrib.pdf.pdf_extractor import PDFExtractor
from magic_doc.conv.base import BaseConv
from magic_doc.progress.filepupdator import FileBaseProgressUpdator


class SingletonModelWrapper:
    _instance = None
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonModelWrapper, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        pass


class Pdf(BaseConv):
    def to_md(self, bits: bytes | str) -> str:
        model_proc  = SingletonModelWrapper()

        return ""