from pathlib import Path
import os

from magic_pdf.dict2md.ocr_mkcontent import union_make
from magic_pdf.libs.MakeContentConfig import MakeMode, DropMode
from magic_pdf.libs.json_compressor import JsonCompressor
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.rw.AbsReaderWriter import AbsReaderWriter
from magic_pdf.pipe.UNIPipe import UNIPipe

from loguru import logger

from magic_doc.conv.base import BaseConv
from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.progress.pupdator import ConvProgressUpdator
from magic_doc.utils.null_writer import NullWriter

NULL_IMG_DIR = "/tmp"

class SingletonModelWrapper:

    def __new__(cls):
        if not hasattr(cls, "instance"):
            from magic_doc.model.doc_analysis_by_pp import PaddleDocAnalysis
            cls.instance = super(SingletonModelWrapper, cls).__new__(cls)
            cls.instance.model = PaddleDocAnalysis(model_load_on_each_gpu_count=int(os.getenv("MODEL_LOAD_ON_GPU", 1)))
        return cls.instance
    
    def __call__(self, bytes: bytes):
        from magic_pdf.model.doc_analyze_by_pp_structurev2 import load_images_from_pdf
        images = load_images_from_pdf(bytes, dpi=200)
        return self.model(images) # type: ignore


class Pdf(BaseConv):
    def to_md(self, bits: bytes | str, pupdator: ConvProgressUpdator) -> str:
        model = SingletonModelWrapper()
        model_list = model(bits)
        pupdator.update(50)
        jso_useful_key = {
            "_pdf_type": "ocr",
            "model_list": model_list,
        }
        image_writer = NullWriter()
        pipe = UNIPipe(bits, jso_useful_key, image_writer, is_debug=True)  # type: ignore
        # pipe.pipe_classify() # 默认ocrpipe的时候不需要再做分类，可以节省时间
        pipe.pipe_parse()
        pupdator.update(100)

        pdf_mid_data = JsonCompressor.decompress_json(pipe.get_compress_pdf_mid_data())
        pdf_info_list = pdf_mid_data["pdf_info"]
        md_content = union_make(pdf_info_list, MakeMode.NLP_MD, DropMode.NONE, NULL_IMG_DIR)
        return md_content  # type: ignore

    def to_mid_result(self, image_writer: AbsReaderWriter, bits: bytes | str, pupdator: ConvProgressUpdator) \
            -> list[dict] | dict:
        model = SingletonModelWrapper()
        pupdator.update(0)
        model_list = model(bits)
        pupdator.update(50)
        jso_useful_key = {
            "_pdf_type": "ocr",
            "model_list": model_list,
        }

        pipe = UNIPipe(bits, jso_useful_key, image_writer, is_debug=True)  # type: ignore
        # pipe.pipe_classify()
        pipe.pipe_parse()
        pupdator.update(100)

        pdf_mid_data = JsonCompressor.decompress_json(pipe.get_compress_pdf_mid_data())
        pdf_info_list = pdf_mid_data["pdf_info"]
        return pdf_info_list


if __name__ == "__main__":
    pupdator = FileBaseProgressUpdator("/tmp/p.txt")
    pdf = Pdf()
    logger.info(
        pdf.to_md(Path(r"D:\project\20231108code-clean\linshixuqiu\pdf_dev\新模型\j.sna.2004.11.030.pdf").read_bytes(), pupdator))
