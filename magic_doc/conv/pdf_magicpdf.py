import os

from magic_pdf.libs.MakeContentConfig import DropMode, MakeMode
from magic_pdf.pipe.UNIPipe import UNIPipe
from magic_pdf.pipe.OCRPipe import OCRPipe
from magic_doc.conv.base import BaseConv
from magic_doc.model.doc_analysis import DocAnalysis, load_images_from_pdf
from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.progress.pupdator import ConvProgressUpdator
from magic_doc.utils import get_repo_directory
from magic_doc.utils.null_writer import NullWriter
from magic_pdf.dict2md.ocr_mkcontent import union_make
from magic_pdf.libs.json_compressor import JsonCompressor
from magic_pdf.rw.AbsReaderWriter import AbsReaderWriter


NULL_IMG_DIR = "/tmp"

class SingletonModelWrapper:

    def __new__(cls):
        if not hasattr(cls, "instance"):
            apply_ocr = os.getenv("APPLY_OCR", "TRUE") == "TRUE" 
            apply_layout = os.getenv("APPLY_LAYOUT", "TRUE") == "TRUE" 
            apply_formula = os.getenv("APPLY_FORMULA", "FALSE") == "TRUE"
            
            cls.instance = super(SingletonModelWrapper, cls).__new__(cls)
            cls.instance.doc_analysis = DocAnalysis(  # type: ignore
                configs=os.path.join(
                    get_repo_directory(), "resources/model/model_configs.yaml"
                ),
                apply_ocr=apply_ocr, apply_layout=apply_layout, apply_formula=apply_formula,
            )
        return cls.instance
    
    def __call__(self, bytes: bytes):
        images = load_images_from_pdf(bytes, dpi=200)
        return self.doc_analysis(images) # type: ignore


class Pdf(BaseConv):
    def to_md(self, bits: bytes | str, pupdator: ConvProgressUpdator) -> str:
        model_proc = SingletonModelWrapper()
        pupdator.update(0)

        model_list = model_proc(bits)  # type: ignore
        pupdator.update(50)
        jso_useful_key = {
            "_pdf_type": "",
            "model_list": model_list,
        }
        image_writer = NullWriter()
        pipe = OCRPipe(bits, model_list, image_writer, is_debug=True)  # type: ignore
        # pipe.pipe_classify() # 默认ocrpipe的时候不需要再做分类，可以节省时间
        pipe.pipe_parse()
        pupdator.update(100)

        pdf_mid_data = JsonCompressor.decompress_json(pipe.get_compress_pdf_mid_data())
        pdf_info_list = pdf_mid_data["pdf_info"]
        md_content = union_make(pdf_info_list, MakeMode.NLP_MD, DropMode.NONE, NULL_IMG_DIR)
        return md_content # type: ignore

    def to_mid_result(self, image_writer: AbsReaderWriter, bits: bytes | str, pupdator: ConvProgressUpdator) -> list[dict] | dict:
        model_proc = SingletonModelWrapper()
        pupdator.update(0)

        model_list = model_proc(bits)  # type: ignore
        pupdator.update(50)
        jso_useful_key = {
            "_pdf_type": "",
            "model_list": model_list,
        }

        pipe = OCRPipe(bits, model_list, image_writer, is_debug=True)  # type: ignore
        pipe.pipe_classify()
        pipe.pipe_parse()
        pupdator.update(100)

        pdf_mid_data = JsonCompressor.decompress_json(pipe.get_compress_pdf_mid_data())
        pdf_info_list = pdf_mid_data["pdf_info"]
        return pdf_info_list

if __name__ == "__main__":
    with open("/opt/data/pdf/20240423/pdf_test2/ol006018w.pdf", "rb") as f:
        bits_data = f.read()
        parser = Pdf()
        md_content = parser.to_md(
            bits_data, FileBaseProgressUpdator("debug/progress.txt")
        )
        with open("debug/pdf2md.by_model.md", "w") as f:
            f.write(md_content) # type: ignore

