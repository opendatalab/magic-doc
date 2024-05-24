from io import BytesIO

from werkzeug.datastructures import FileStorage

from magic_doc.contrib.pdf.pdf_extractor import PDFExtractor
from magic_doc.conv.base import BaseConv
from magic_doc.progress.filepupdator import FileBaseProgressUpdator
from magic_doc.progress.pupdator import ConvProgressUpdator


class Pdf(BaseConv):
    def to_md(self, bits: bytes | str, pupdator: ConvProgressUpdator) -> str:
        # TODO: 单例化模型
        pdf_extractor = PDFExtractor()
        buf = BytesIO(bits)  # type: ignore
        content = pdf_extractor.run("stream io data", FileStorage(buf, "fake.pdf"))
        arr = []
        pupdator.update(0)

        N = len(content)
        progress_h = {N * i // 100: 1 for i in range(10, 100, 10)}
        for idx, page in enumerate(content):
            if idx in progress_h:
                pupdator.update(idx * 100 // N)
            for record in page.get("content_list", []):
                arr.append(record.get("data", ""))
        pupdator.update(100)
        return "\n\n".join(arr)


if __name__ == "__main__":
    if 1:
        with open("/opt/data/pdf/20240423/pdf_test2/ol006018w.pdf", "rb") as f:
            bits_data = f.read()
            parser = Pdf()
            md_content = parser.to_md(bits_data, FileBaseProgressUpdator("debug/progress.txt"))

        with open("debug/pdf2md.md", "w") as f:
            f.write(md_content)
