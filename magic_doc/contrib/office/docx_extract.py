import xml.etree.ElementTree as ET
import zipfile

from pathlib import Path
from magic_doc.contrib.model import ExtractResponse, Content, Page
from magic_doc.contrib.office import OfficeExtractor
from typing import IO
from werkzeug.datastructures import FileStorage


class DocxExtractor(OfficeExtractor):
    def __init__(self) -> None:
        super().__init__()

    def setup(self):
        pass

    def __word2markdown(
        self,
        id: str,
        docx_file_stream: IO[bytes],
        save_fig_dir,
    ):
        tag_w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        tag_body = f"{tag_w}body"

        content_list = []
        with zipfile.ZipFile(docx_file_stream, "r") as docx:
            xml_content = docx.read("word/document.xml")
            tree = ET.XML(xml_content)
            body = tree.find(tag_body)

            for child in body:
                tag = child.tag.split("}")[-1]
                match tag:
                    case "p":
                        text = ""
                        for ele in child.iter():
                            if t := ele.text:
                                if len(t) > 0:
                                    text += t
                        text = text.strip()
                        if len(text) > 0:
                            content_list.append(Content(type="text", data=text+"\n"))
                    case "tbl":
                        col_size = len(list(child.find(f"{tag_w}tblGrid")))
                        md = "\n"
                        for idx, row in enumerate(child.iter(f"{tag_w}tr")):
                            if idx == 1:
                                md += "|"
                                for _ in range(col_size):
                                    md += "---|"
                                md += "\n"
                            md += "|"
                            # print(row)
                            for cell in row.iter(f"{tag_w}tc"):
                                t = ""
                                for cell_ele in cell.itertext():
                                    t += (
                                        cell_ele.strip()
                                        .replace("\r", "")
                                        .replace("\n", "")
                                    )
                                md += f" {t} |"
                            md += "\n"
                        md += "\n"
                        content_list.append(Content(type="md", data=md))
                    case "sectPr":
                        # docx section pointer, meaningless
                        pass
                    case unknown:
                        print(unknown)
            return content_list

    def extract(
        self,
        r: FileStorage | Path,
        id: str,
        dir: Path,
        media_dir: Path,
        skip_image: bool,
    ) -> ExtractResponse:
        if type(r) is FileStorage:
            page = Page(
                page_no=0,
                content_list=self.__word2markdown(id, r.stream, media_dir),
            )
        else:
            page = Page(
                page_no=0,
                content_list=self.__word2markdown(id, open(r, "rb"), media_dir),
            )
        self.clean_up(id)
        return [page]


if __name__ == "__main__":
    e = DocxExtractor()

    res = e.run(
        "def",
        Path(
            "test_data/doc/【中简】模电自测第四版.docx",
        ),
    )

    print(res)

    e.wait_all()
