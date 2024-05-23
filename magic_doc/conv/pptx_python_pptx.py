import tempfile
from pathlib import Path

from loguru import logger

from magic_doc.contrib.office.pptx_extract import PptxExtractor
from magic_doc.conv.base import BaseConv
from magic_doc.progress.pupdator import ConvProgressUpdator


class Pptx(BaseConv):
    def __init__(self, pupdator: ConvProgressUpdator):
        super().__init__(pupdator)

    def to_md(self, bits: bytes) -> str:
        mid_json = self.pptx_to_contentlist(bits)
        md_content_list = []
        for page in mid_json:
            page_content_list = page['content_list']
            total = len(page_content_list)
            for index, content in enumerate(page_content_list):
                progress = 50 + int(index / total * 50)
                # logger.info(f"progress: {progress}")
                self._progress_updator.update(progress)
                if content['type'] == 'image':
                    pass
                elif content['type'] == "text":
                    data = content['data']
                    md_content_list.append(data)
        return "\n".join(md_content_list)

    def pptx_to_contentlist(self, bits):
        with tempfile.TemporaryDirectory() as temp_path:
            temp_dir = Path(temp_path)
            media_dir = temp_dir / "media"
            media_dir.mkdir()
            file_path = temp_dir / "tmp.pptx"
            file_path.write_bytes(bits)
            pptx_extractor = PptxExtractor()
            pages = pptx_extractor.extract(file_path, "tmp", temp_dir, media_dir, True)
            self._progress_updator.update(50)
            return pages


if __name__ == '__main__':
    pupdator = ConvProgressUpdator()
    logger.info(
        Pptx(pupdator).to_md(open(r"D:\project\20240514magic_doc\doc_ppt\doc\【英文-模板】Professional Pack Standard.pptx", "rb").read()))
