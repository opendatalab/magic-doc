from pathlib import Path

from magic_pdf.dict2md.ocr_mkcontent import union_make
from magic_pdf.libs.MakeContentConfig import MakeMode, DropMode
from magic_pdf.libs.json_compressor import JsonCompressor
from magic_pdf.model.doc_analyze_by_pp_structurev2 import doc_analyze
from magic_pdf.rw.AbsReaderWriter import AbsReaderWriter

from loguru import logger

from magic_doc.conv.base import BaseConv
from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.progress.pupdator import ConvProgressUpdator
from magic_doc.utils.null_writer import NullWriter

from magic_pdf.pipe.UNIPipe import UNIPipe

NULL_IMG_DIR = "/tmp"

class Pdf(BaseConv):
    def to_md(self, bits: bytes | str, pupdator: ConvProgressUpdator) -> str:

        model_list = doc_analyze(bits, ocr=True)
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

        pupdator.update(0)

        model_list = doc_analyze(bits, ocr=True)  # type: ignore
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
