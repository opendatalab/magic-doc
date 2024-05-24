import os
import tempfile
from pathlib import Path
from subprocess import Popen

from loguru import logger

from magic_doc.contrib.model import Page
from magic_doc.contrib.office.docx_extract import DocxExtractor
from magic_doc.conv.base import BaseConv
from magic_doc.progress.pupdator import ConvProgressUpdator


class Doc(BaseConv):

    def __init__(self, pupdator: ConvProgressUpdator):
        super().__init__(pupdator)

    def to_md(self, bits: bytes) -> str:
        page_list = self.doc_to_pagelist(bits)
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

    def doc_to_docx(self, doc_path: str, dir_path: str) -> str:
        cmd = f'soffice --headless --convert-to docx "{doc_path}" --outdir "{dir_path}"'
        logger.info(cmd)
        process = Popen(cmd, shell=True)
        process.wait()
        fname = str(Path(doc_path).stem)
        docx_path = os.path.join(os.path.dirname(doc_path), f'{fname}.docx')
        if not os.path.exists(docx_path):
            # logger.error(f"> !!! File conversion failed {doc_path} ==> {docx_path}")
            raise Exception(f"> !!! File conversion failed {doc_path} ==> {docx_path}")
        else:
            return docx_path

    def doc_to_pagelist(self, bits) -> list[Page]:
        with tempfile.TemporaryDirectory() as temp_path:
            temp_dir = Path(temp_path)
            media_dir = temp_dir / "media"
            media_dir.mkdir()
            file_path = temp_dir / "tmp.doc"
            file_path.write_bytes(bits)
            docx_file_path = self.doc_to_docx(str(file_path), str(temp_path))
            self._progress_updator.update(50)
            docx_extractor = DocxExtractor()
            pages = docx_extractor.extract(Path(docx_file_path), "tmp", temp_dir, media_dir, True)
            self._progress_updator.update(80)
            return pages


if __name__ == '__main__':
    pupdator = ConvProgressUpdator()
    doc = Doc(pupdator)
    logger.info(doc.to_md(Path(r"D:\project\20240514magic_doc\doc_ppt\doc\demo\文本+表+图1.doc").read_bytes()))
