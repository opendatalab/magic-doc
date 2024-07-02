import io
import os
import requests


from pathlib import Path
from typing import IO, List
from zipfile import ZipFile
from loguru import logger

from werkzeug.datastructures import FileStorage

from magic_doc.contrib.office import OfficeExtractor
from magic_doc.contrib.model import ExtractResponse, Content, Page
from pedia_document_parser.config import Config

ext_map: dict[str, str] = {
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def extract_office_to_dir(
    file_bytes: IO[bytes],
    ext: str,
    dir: Path,
    media_dir: Path,
    skip_image: bool,
):
    config = Config()
    data = file_bytes.read()

    if skip_image:
        headers = {
            "Content-type": ext_map[ext],
            "Accept": "application/json",
            "X-Tika-Skip-Embedded": "true",
        }
        response = requests.put(
            f"{config.tika}/tika/text",
            headers=headers,
            data=data,
        )
        content: str = response.json()["X-TIKA:content"]

        with dir.joinpath("__TEXT__").open("w") as f:
            f.write(content)

        return

    headers = {
        "Content-type": ext_map[ext],
        "Accept": "application/zip",
    }
    response = requests.put(
        f"{config.tika}/unpack/all",
        headers=headers,
        data=data,
    )

    if not response.ok:
        raise Exception(f"tika failed {response.text}")

    with ZipFile(io.BytesIO(response.content), "r") as zip:
        for zipped_file in zip.namelist():
            with zip.open(zipped_file, "r") as f:
                if zipped_file == "__TEXT__" or zipped_file == "__METADATA__":
                    dir.joinpath(zipped_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(dir.joinpath(zipped_file), "wb") as w:
                        w.write(f.read())
                else:
                    media_dir.joinpath(zipped_file).parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )
                    with open(media_dir.joinpath(zipped_file), "wb") as w:
                        w.write(f.read())
            logger.debug(f"save file {zipped_file}")


def list_files_recursive(root: Path) -> List[Path]:
    result = []
    for entry in os.listdir(root):
        full_path = root.joinpath(entry)
        if os.path.isdir(full_path):
            result.extend(list_files_recursive(full_path))
        else:
            result.append(full_path)
    return result


class GeneralOfficeExtractor(OfficeExtractor):
    def __init__(self) -> None:
        super().__init__()

    def setup(self):
        pass

    def extract(
        self,
        r: FileStorage | Path,
        id: str,
        dir: Path,
        media_dir: Path,
        skip_image: bool,
    ) -> ExtractResponse:
        if type(r) is FileStorage:
            r.name = os.path.basename(r.filename)

        ext: str = os.path.splitext(r.name)[1]
        ext = ext.lower()

        if ext not in ext_map:
            raise Exception(f"{ext} not supported")

        if type(r) is FileStorage:
            extract_office_to_dir(r.stream, ext, dir, media_dir, skip_image)
        elif issubclass(type(r), Path):
            extract_office_to_dir(open(r, "rb"), ext, dir, media_dir, skip_image)
        else:
            raise Exception(type(r))

        page = Page(page_no=0, content_list=[])

        media_map: dict[Path, str] = {}
        for media_file in list_files_recursive(media_dir):
            media_map[media_file] = self.generate_img_path(id, media_file.name)

        match ext:
            case ".pptx" | ".ppt":
                with open(dir.joinpath("__TEXT__"), "r") as f:
                    text: str = f.read()

                content_list = [Content(type="text", data=text)]
                page["content_list"] = content_list

                self.upload_background(id, media_map)

                return [page]
                # texts: list[str] = text.split("\n")
                # new_texts: list[str] = []

                # enters = 0
                # for text in texts:
                #     if len(text.strip()) == 0:
                #         enters += 1
                #         if enters <= 3:
                #             new_texts.append("")
                #     else:
                #         enters = 0
                #         new_texts.append(text)

                # texts = "\n".join(new_texts).replace("\n\n\n","\npage_break\n").split("\n")

                # pages = [Page(page_no=0, content_list=[])]
                # for text in texts:
                #     if text == "page_break":
                #         page = Page(page_no=len(pages), content_list=[])
                #         pages.append(page)
                #     else:
                #         pages[len(pages) - 1]["content_list"].append(
                #             Content(type="text", data=text)
                #         )

                # page = Page(page_no=len(pages), content_list=[])

                # img_map = {}
                # for pic_file in media_dir.glob("*"):
                #     img_map[pic_file] = self.generate_img_path(id, pic_file.name)
                #     page["content_list"].append(
                #         Content(type="image", data=img_map[pic_file])
                #     )

                # pages.append(page)
                # self.upload_background(id, media_map)

                # return pages
            case ".doc" | ".docx":
                with open(dir.joinpath("__TEXT__"), "r") as f:
                    text = f.read()

                content_list = [Content(type="text", data=text)]

                for media_file, s3_path in media_map.items():
                    new_content_list = []

                    for content in content_list:
                        if content["type"] != "text":
                            new_content_list.append(content)
                            continue

                        pos = content["data"].find(media_file.name)
                        if pos == -1:
                            new_content_list.append(content)
                            continue

                        lpos = content["data"][:pos].rindex("[")

                        assert lpos != -1

                        r_text = content["data"][pos + len(media_file.name) + 1 :]
                        l_text = content["data"][:lpos]

                        new_content_list.append(Content(type="text", data=l_text))
                        new_content_list.append(Content(type="image", data=s3_path))
                        new_content_list.append(Content(type="text", data=r_text))

                    content_list = new_content_list

                page["content_list"] = content_list

                self.upload_background(id, media_map)

                return [page]

