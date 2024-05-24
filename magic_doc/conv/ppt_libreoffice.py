import os
from subprocess import Popen
import tempfile
from pathlib import Path

from loguru import logger

from magic_doc.contrib.model import Page
from magic_doc.contrib.office.pptx_extract import PptxExtractor
from magic_doc.conv.base import BaseConv
from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.progress.pupdator import ConvProgressUpdator


class Ppt(BaseConv):
    def __init__(self):
        super().__init__()

    def to_md(self, bits: bytes, pupdator: ConvProgressUpdator) -> str:
        page_list = self.ppt_to_pagelist(bits, pupdator)
        md_content_list = []
        total = len(page_list)
        for index, page in enumerate(page_list):
            progress = 80 + int(index / total * 20)
            # logger.info(f"progress: {progress}")
            page_content_list = page['content_list']
            for content in page_content_list:
                pupdator.update(progress)
                if content['type'] == 'image':
                    pass
                elif content['type'] == "text":
                    data = content['data']
                    md_content_list.append(data)
        return "\n".join(md_content_list)

    def ppt_to_pptx(self, ppt_path: str, dir_path: str) -> str:
        cmd = f'soffice --headless --convert-to pptx "{ppt_path}" --outdir "{dir_path}"'
        logger.info(cmd)
        process = Popen(cmd, shell=True)
        process.wait()
        fname = str(Path(ppt_path).stem)
        pptx_path = os.path.join(os.path.dirname(ppt_path), f'{fname}.pptx')
        if not os.path.exists(pptx_path):
            # logger.error(f"> !!! File conversion failed {ppt_path} ==> {pptx_path}")
            raise Exception(f"> !!! File conversion failed {ppt_path} ==> {pptx_path}")
        else:
            return pptx_path

    def ppt_to_pagelist(self, bits, pupdator: ConvProgressUpdator) -> list[Page]:
        with tempfile.TemporaryDirectory() as temp_path:
            temp_dir = Path(temp_path)
            media_dir = temp_dir / "media"
            media_dir.mkdir()
            file_path = temp_dir / "tmp.ppt"
            file_path.write_bytes(bits)
            pptx_file_path = self.ppt_to_pptx(str(file_path), str(temp_path))
            pupdator.update(50)
            pptx_extractor = PptxExtractor()
            pages = pptx_extractor.extract(Path(pptx_file_path), "tmp", temp_dir, media_dir, True)
            pupdator.update(80)
            return pages


if __name__ == '__main__':
    pupdator = FileBaseProgressUpdator("/tmp/p.txt")
    ppt = Ppt()
    logger.info(
        ppt.to_md(
            open(r"D:\project\20240514magic_doc\doc_ppt\doc\【英文-课件】MIT15_082JF10_lec10.3MB.ppt", "rb").read(), pupdator))
