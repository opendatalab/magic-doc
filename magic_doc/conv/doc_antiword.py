import os
import tempfile
from pathlib import Path

from loguru import logger

from magic_doc.contrib.model import Page
from magic_doc.contrib.office.doc import DocExtractor
from magic_doc.conv.base import BaseConv
from magic_doc.progress.pupdator import ConvProgressUpdator


class Doc(BaseConv):

    def __init__(self, pupdator: ConvProgressUpdator):
        super().__init__(pupdator)

    def to_md(self, bits: bytes) -> str:
        mid_json = self.doc_to_contentlist(bits)
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

    def doc_to_contentlist(self, bits) -> list[Page]:
        with tempfile.TemporaryDirectory() as temp_path:
            temp_dir = Path(temp_path)
            media_dir = temp_dir / "media"
            media_dir.mkdir()
            file_path = temp_dir / "tmp.doc"
            file_path.write_bytes(bits)
            doc_extractor = DocExtractor()
            cwd_path = os.path.dirname(os.path.abspath(__file__)) / Path("../bin/linux")
            bin_path = cwd_path / "antiword"
            os.chmod(bin_path, 0o755)
            contentlist = doc_extractor.extract(file_path, "1", temp_dir, media_dir, True, cwd_path=cwd_path)
            self._progress_updator.update(50)
        return contentlist


if __name__ == '__main__':
    pupdator = ConvProgressUpdator()
    doc = Doc(pupdator)
    logger.info(doc.to_md(Path("/home/myhloli/文本+表+图1.doc").read_bytes()))
