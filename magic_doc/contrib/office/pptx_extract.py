import json
import sys

from pathlib import Path
from typing import List

from loguru import logger
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.parts.image import Image
from pptx.presentation import Presentation as ppt
from pptx.shapes.autoshape import Shape
from pptx.shapes.picture import Picture
from pptx.shapes.graphfrm import GraphicFrame
from pptx.table import Table, _Row, _Cell
from pptx.slide import Slide
from pptx.shapes.group import GroupShape
from werkzeug.datastructures import FileStorage

from magic_doc.contrib.office import OfficeExtractor
from magic_doc.contrib.model import ExtractResponse, Page, Content


class PptxExtractor(OfficeExtractor):
    def __init__(self) -> None:
        super().__init__()

    def setup(self):
        pass

    def handle_shape(
        self,
        shape: Shape,
        content_list: List[Content],
        media_dir: Path,
        img_map: dict[Path, str],
        id: str,
        skip_image: bool,
    ):
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                content_list.append(
                    Content(
                        type="text",
                        data=paragraph.text + "\n",
                    )
                )
        elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE and not skip_image:
            shape: Picture
            image: Image = shape.image
            image_bytes = image.blob
            img_path = media_dir.joinpath(f"pic-{len(img_map)}.{image.ext}")
            img_s3_path = self.generate_img_path(id, img_path.name)
            img_map[img_path] = img_s3_path
            content_list.append(Content(type="image", data=img_s3_path))
            with open(img_path, "wb") as file:
                file.write(image_bytes)
        elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
            shape: GraphicFrame
            table: Table = shape.table
            md = "\n"
            for row_no, row in enumerate(table.rows):
                row: _Row
                md += "|"
                if row_no == 1:
                    for col in row.cells:
                        md += "---|"
                    md += "\n|"
                for col in row.cells:
                    cell: _Cell = col
                    md += " " + cell.text.replace("\r", " ").replace("\n", " ") + " |"
                md += "\n"
            md += "\n"
            content_list.append(Content(type="md", data=md))
        elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            shape: GroupShape
            for sub_shape in shape.shapes:
                self.handle_shape(sub_shape, content_list, media_dir, img_map, id, skip_image)
        else:
            # print(shape.shape_type, type(shape), file=sys.stderr)
            pass

    def extract(
        self,
        r: FileStorage | Path,
        id: str,
        dir: Path,
        media_dir: Path,
        skip_image: bool,
    ) -> ExtractResponse:
        pages = []
        img_map = {}

        presentation: ppt = Presentation(r)
        for page_no, slide in enumerate(presentation.slides):
            slide: Slide
            page = Page(page_no=page_no, content_list=[])
            for shape in slide.shapes:
                self.handle_shape(
                    shape,
                    page["content_list"],
                    media_dir,
                    img_map,
                    id,
                    skip_image,
                )

            pages.append(page)

        # self.upload_background(id, img_map)

        return pages


if __name__ == "__main__":
    e = PptxExtractor()
    # from pedia_document_parser.s3.client import get_s3_client

    # cli = get_s3_client()

    # data = cli.read_object(
    #     "s3://pedia-document-parser/office-doucments/【英文-模板】Professional Pack Standard.pptx"
    # )
    # with open("1.pptx", "wb") as f:
    #     f.write(data.read())

    x = e.run(
        "ghi",
        Path("test_data/doc/商业项目市场分析与产品定位报告.pptx"),
    )
    content = ""
    for p in x:
        content += f"\n====== page {p['page_no']} ======\n"
        for pp in p["content_list"]:
            content += pp["data"]

    print(content)

    # cli.read_object("s3://pedia-document-parser/office-doucments/【英文-课件】MIT15_082JF10_av.pptx")

    # print(
    #     json.dumps(
    #         e.run(
    #             "ghi",
    #             Path(
    #                 "/home/SENSETIME/wuziming/doc/doc/【英文-模板】Professional Pack Standard.pptx",
    #             ),
    #         ),
    #         ensure_ascii=False,
    #         indent=4,
    #     )
    # )
    e.wait_all()
