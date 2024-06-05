from io import BytesIO

from loguru import logger
from magic_pdf.dict2md.ocr_mkcontent import union_make
from magic_pdf.libs.MakeContentConfig import MakeMode, DropMode
from magic_pdf.libs.json_compressor import JsonCompressor
from werkzeug.datastructures import FileStorage

from magic_doc.contrib.pdf.pdf_extractor import PDFExtractor
from magic_doc.conv.base import BaseConv
from magic_doc.conv.pdf_magicpdf import SingletonModelWrapper
from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.progress.pupdator import ConvProgressUpdator
from magic_doc.utils.null_writer import NullWriter
from magic_pdf.pipe.OCRPipe import OCRPipe

class Pdf(BaseConv):
    def to_md(self, bits: bytes | str, pupdator: ConvProgressUpdator) -> str:
        # TODO: 单例化模型
        pdf_extractor = PDFExtractor()
        buf = BytesIO(bits)  # type: ignore
        content = pdf_extractor.run("stream io data", FileStorage(buf, "fake.pdf"))
        arr = []
        pupdator.update(0)

        N = len(content)
        progress_h = {N * i // 100: 1 for i in range(10, 100, 10)}
        for idx, page in enumerate(content):
            if idx in progress_h:
                pupdator.update(idx * 100 // N)
            for record in page.get("content_list", []):
                arr.append(record.get("data", ""))

        text_all = ""
        for content in arr:
            text_all += content

        def calculate_not_printable_rate(text):
            printable = sum(1 for c in text if c.isprintable())
            total = len(text)
            if total == 0:
                return 0  # 避免除以零的错误
            return (total - printable) / total
        not_printable_rate = calculate_not_printable_rate(text_all)
        if not_printable_rate > 0.02:
            # pdf可能是乱码，切换到ocr处理
            logger.info("switch to ocrpipe by garbled check")
            model_proc = SingletonModelWrapper()
            model_list = model_proc(bits)  # type: ignore
            pupdator.update(50)
            image_writer = NullWriter()
            pipe = OCRPipe(bits, model_list, image_writer, is_debug=True)  # type: ignore
            pipe.pipe_parse()
            pdf_mid_data = JsonCompressor.decompress_json(pipe.get_compress_pdf_mid_data())
            pdf_info_list = pdf_mid_data["pdf_info"]
            NULL_IMG_DIR = "/tmp"
            md_content = union_make(pdf_info_list, MakeMode.NLP_MD, DropMode.NONE, NULL_IMG_DIR)
            pupdator.update(100)
            return md_content
        else:
            pupdator.update(100)
            return "\n\n".join(arr)


if __name__ == "__main__":
    if 1:
        with open("/opt/data/pdf/20240423/pdf_test2/ol006018w.pdf", "rb") as f:
            bits_data = f.read()
            parser = Pdf()
            md_content = parser.to_md(bits_data, FileBaseProgressUpdator("debug/progress.txt"))

        with open("debug/pdf2md.md", "w") as f:
            f.write(md_content)
