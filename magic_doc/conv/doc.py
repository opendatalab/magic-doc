import os
import tempfile
from pathlib import Path

from loguru import logger

from magic_doc.contrib.model import Page
from magic_doc.contrib.office.doc import DocExtractor
from magic_doc.conv.base import BaseConv


class Doc(BaseConv):
    def to_md(self, bits: bytes) -> str:
        mid_json = self.doc_to_contentlist(bits)
        md_content_list = []
        for page in mid_json:
            page_content_list = page['content_list']
            for content in page_content_list:
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
            if not media_dir.exists():
                media_dir.mkdir()
            file_path = temp_dir / "tmp.doc"
            if file_path.exists():
                os.remove(file_path)
            file_path.write_bytes(bits)
            doc_extractor = DocExtractor()
            cwd_path = Path.cwd() / Path("../bin/linux") # TODO pip之后路径还对吗
            bin_path = cwd_path / "antiword"
            os.chmod(bin_path, 0o755)
            contentlist = doc_extractor.extract(file_path, "1", temp_dir, media_dir, True, cwd_path=cwd_path)

        return contentlist


if __name__ == '__main__':
    doc = Doc()
    logger.info(doc.to_md(Path("/home/myhloli/文本+表+图1.doc").read_bytes()))