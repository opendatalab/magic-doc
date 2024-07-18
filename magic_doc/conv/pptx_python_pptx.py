import tempfile
from pathlib import Path

from loguru import logger

from magic_doc.contrib.model import Page
from magic_doc.contrib.office.pptx_extract import PptxExtractor
from magic_doc.conv.base import BaseConv
from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.progress.pupdator import ConvProgressUpdator


class Pptx(BaseConv):
    def __init__(self):
        super().__init__()

    def to_md(self, bits: bytes, pupdator: ConvProgressUpdator) -> str:
        page_list = self.pptx_to_pagelist(bits, pupdator)
        md_content_list = []
        total = len(page_list)
        for index, page in enumerate(page_list):
            progress = 50 + int(index / total * 50)
            # logger.info(f"progress: {progress}")
            page_content_list = page["content_list"]
            for content in page_content_list:
                pupdator.update(progress)
                if content["type"] == "image":
                    pass
                elif content["type"] == "text":
                    data = content["data"]
                    md_content_list.append(data)
        return "\n".join(md_content_list)

    def pptx_to_pagelist(self, bits, pupdator: ConvProgressUpdator) -> list[Page]:
        with tempfile.TemporaryDirectory() as temp_path:
            temp_dir = Path(temp_path)
            media_dir = temp_dir / "media"
            media_dir.mkdir()
            file_path = temp_dir / "tmp.pptx"
            file_path.write_bytes(bits)
            pptx_extractor = PptxExtractor()
            pages = pptx_extractor.extract(file_path)
            pupdator.update(50)
            return pages


if __name__ == "__main__":
    pupdator = FileBaseProgressUpdator("/tmp/p.txt")
    pptx = Pptx()
    if 0:
        logger.info(
            pptx.to_md(
                open(
                    r"D:\project\20240514magic_doc\doc_ppt\doc\【英文-模板】Professional Pack Standard.pptx",
                    "rb",
                ).read(),
                pupdator,
            )
        )
    if 0:
        print(
            pptx.to_md(
                open(
                    r"/opt/data/magic_doc/20240605/doc/【英文-模板】Professional Pack Standard.pptx",
                    "rb",
                ).read(),
                pupdator,
            )
        )
    if 1:
        print(
            pptx.to_md(
                open(
                    r"/home/PJLAB/xurui1/Git/Magic-Doc/MIT15_082JF10_lec10.3MB.pptx",
                    "rb",
                ).read(),
                pupdator,
            )
        )
