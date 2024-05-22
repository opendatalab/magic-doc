import os
import shutil
from pathlib import Path

from magic_doc.contrib.model import Page
from magic_doc.contrib.office.doc import DocExtractor
from magic_doc.conv.base import Base


class Doc(Base):
    def to_md(self, bits: bytes) -> str:
        content_list = self.doc_to_contentlist(bits)
        return "\n".join([c['data'] for c in content_list])

    def doc_to_contentlist(self, bits) -> list[Page]:

        temp_dir = Path("/tmp")
        pic_dir = temp_dir / "pic"
        if not Path(pic_dir).exists():
            pic_dir.mkdir()
        shutil.rmtree(pic_dir)
        text_path = temp_dir / "text"
        if text_path.exists():
            os.remove(text_path)
        file_path = temp_dir / "tmp.doc"
        if file_path.exists():
            os.remove(file_path)
        file_path.write_bytes(bits)
        doc_extractor = DocExtractor()
        cwd_path = Path.cwd() / Path("../bin/linux")
        bin_path = cwd_path / "antiword"
        os.chmod(bin_path, 0o755)
        contentlist = doc_extractor.extract(file_path, "1", temp_dir, temp_dir, True, cwd_path=cwd_path)

        return contentlist


if __name__ == '__main__':
    doc = Doc()
    print(doc.to_md(Path(r"D:\project\20240514magic_doc\doc_ppt\doc\demo\文本+表+图1.doc").read_bytes()))