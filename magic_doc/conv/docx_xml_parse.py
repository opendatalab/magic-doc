import io
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from loguru import logger

from magic_doc.contrib.model import Content, Page
from magic_doc.contrib.office.docx_extract import DocxExtractor
from magic_doc.conv.base import BaseConv
from magic_doc.progress.pupdator import ConvProgressUpdator


class Docx(BaseConv):
    def __init__(self, pupdator: ConvProgressUpdator):
        super().__init__(pupdator)

    def to_md(self, bits: bytes) -> str:
        page_list = self.docx_to_pagelist(bits)
        md_content_list = []
        for page in page_list:
            page_content_list = page['content_list']
            total = len(page_content_list)
            for index, content in enumerate(page_content_list):
                progress = 50 + int(index / total * 50)
                # logger.info(f"progress: {progress}")
                self._progress_updator.update(progress)
                if content['type'] == 'image':
                    pass
                elif content['type'] in ["text", "md"]:
                    data = content['data']
                    md_content_list.append(data)
        return "\n".join(md_content_list)

    def docx_to_pagelist(self, bits) -> list[Page]:
        with tempfile.TemporaryDirectory() as temp_path:
            temp_dir = Path(temp_path)
            media_dir = temp_dir / "media"
            media_dir.mkdir()
            file_path = temp_dir / "tmp.docx"
            file_path.write_bytes(bits)
            docx_extractor = DocxExtractor()
            pages = docx_extractor.extract(file_path, "tmp", temp_dir, media_dir, True)
            self._progress_updator.update(50)
            return pages


if __name__ == '__main__':
    pupdator = ConvProgressUpdator()
    logger.info(
        Docx(pupdator).to_md(open(r"D:\project\20240514magic_doc\doc_ppt\doc\demo\文本+表+图.docx", "rb").read()))
