from io import BytesIO

from werkzeug.datastructures import FileStorage

from magic_doc.contrib.pdf.pdf_extractor import PDFExtractor
from magic_doc.conv.base import Base


class Pdf(Base):
    def to_md(self, bits: bytes | str) -> str:
        # TODO: 单例化模型
        pdf_extractor = PDFExtractor()
        buf = BytesIO(bits)  # type: ignore
        content = pdf_extractor.run("stream io data", FileStorage(buf, "fake.pdf"))
        arr = []
        for page in content:
            for record in page.get("content_list", []):
                arr.append(record.get("data", ""))
        return "\n\n".join(arr)


if __name__ == "__main__":
    if 1:
        with open("/opt/data/pdf/20240423/pdf_test2/ol006018w.pdf", "rb") as f:
            bits_data = f.read()
            parser = Pdf()
            md_content = parser.to_md(bits_data)

        with open("debug/pdf2md.md", "w") as f:
            f.write(md_content)
            



