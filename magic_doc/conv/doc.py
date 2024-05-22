import tempfile
from pathlib import Path

from magic_doc.contrib.model import Page
from magic_doc.contrib.office.doc import DocExtractor
from magic_doc.conv.base import Base


class Doc(Base):
    def to_md(self, bits: bytes) -> str:
        content_list = self.doc_to_contentlist(bits)
        return "\n".join([c['data'] for c in content_list])

    def doc_to_contentlist(self, bits) -> list[Page]:
        with tempfile.TemporaryDirectory() as tmpdirname:
            temp_dir = Path(tmpdirname)
            file_path = temp_dir / "tmp.doc"
            file_path.write_bytes(bits)
            doc_extractor = DocExtractor()
            bin_path = Path("../bin/linux")
            cwd_path = Path.cwd() / bin_path
            pic_dir = temp_dir / "pic"
            if not Path(pic_dir).exists():
                pic_dir.mkdir()
            contentlist = doc_extractor.extract(file_path, "1", temp_dir, temp_dir, True, cwd_path=cwd_path)

        return contentlist


if __name__ == '__main__':
    doc = Doc()
    print(doc.to_md(Path(r"D:\project\20240514magic_doc\doc_ppt\doc\demo\文本+表+图1.doc").read_bytes()))