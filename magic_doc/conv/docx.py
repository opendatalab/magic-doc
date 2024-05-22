import io
import zipfile
import xml.etree.ElementTree as ET

from loguru import logger

from magic_doc.contrib.model import Content
from magic_doc.conv.base import Base


class Docx(Base):
    def to_md(self, bits: bytes) -> str:
        content_list = self.docx_to_contentlist(bits)
        return "\n".join([c['data'] for c in content_list])

    def docx_to_contentlist(self, bits) -> list[Content]:
        tag_w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        tag_body = f"{tag_w}body"

        content_list = []
        with io.BytesIO(bits) as zip_file:
            with zipfile.ZipFile(zip_file, 'r') as docx:
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
                                content_list.append(Content(type="text", data=text + "\n"))
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

if __name__ == '__main__':
    logger.info(Docx().to_md(open(r"D:\project\20240514magic_doc\doc_ppt\doc\demo\文本+表+图.docx", "rb").read()))
