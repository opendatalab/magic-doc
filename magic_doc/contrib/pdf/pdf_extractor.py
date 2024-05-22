import random
import fitz

from magic_doc.contrib.model import (
    ExtractResponse,
    Extractor,
    Page,
    Content,
)
from magic_doc.contrib.wrapper_exceptions import NotSupportOcrPDFException

from werkzeug.datastructures import FileStorage
from loguru import logger


class PDFExtractor(Extractor):
    def __init__(self) -> None:
        super().__init__()

    def setup(self):
        pass

    def is_digital(self, doc, check_page=10, text_len_thrs=100):
        sample_page_num = min(check_page, doc.page_count)
        page_ids = random.sample(range(doc.page_count), sample_page_num)
        page_text_len = [
            len(doc[pno].get_text("text")) > text_len_thrs for pno in page_ids
        ]
        if any(page_text_len):
            return True
        return False

    # Guess kimi implemetation
    def get_text_with_pymupdf(self, doc):
        pages = []
        page_no = 0
        for page in doc:
            content_list = []
            for block in page.get_text("blocks"):
                x0, y0, x1, y1, block_text, block_no, block_type = block
                lf_count = 0
                for ch in block_text:
                    if ch == "\n":
                        lf_count += 1
                block_text = (
                    block_text.replace("-\n", "")
                    .replace("´\n", "´")
                    .replace(" \n", " ")
                )
                if lf_count >= 2:
                    block_text = block_text.replace("\n", " ").strip()
                if len(block_text.strip()) == 0:
                    continue
                content_list.append(
                    Content(
                        type="text",
                        data=block_text,
                    )
                )
            pages.append(Page(page_no=page_no, content_list=content_list))
            page_no += 1
        return pages

    def run(
        self, file_parse_id: str, r: FileStorage, skip_image: bool = True
    ) -> ExtractResponse:
        file_content = r.stream.read()
        with fitz.open(stream=file_content) as doc:
            if self.is_digital(doc):
                logger.info(f"{file_parse_id} is digital pdf")
                return self.get_text_with_pymupdf(doc)
        raise NotSupportOcrPDFException


if __name__ == "__main__":
    pdf_extractor = PDFExtractor()
    with open("magic_doc/contrib/test_data/pdf/test.pdf", "rb") as f:
        logger.info(pdf_extractor.run("test", FileStorage(f, filename="STL.pdf")))
