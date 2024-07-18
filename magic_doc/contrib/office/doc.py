import shutil
import json

from loguru import logger
from pathlib import Path
from subprocess import Popen, PIPE

from werkzeug.datastructures import FileStorage

from magic_doc.contrib.office import OfficeExtractor
from magic_doc.contrib.model import Page, Content, ExtractResponse


class DocExtractor(OfficeExtractor):
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
        cwd_path="/opt/antiword"
    ) -> ExtractResponse:
        doc_path = dir.joinpath("its.doc")

        if type(r) is FileStorage:
            r.save(doc_path)
        else:
            shutil.copyfile(r, doc_path)

        if skip_image:
            cmd = f"./antiword -f -i 1 -o {dir.as_posix()} {doc_path.as_posix()}"
        else:
            cmd = f"./antiword -f -i 3 -o {dir.as_posix()} {doc_path.as_posix()}"
        logger.info(f"cmd: {cmd}")
        process = Popen(cmd, shell=True, cwd=Path(cwd_path), stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        process.wait()

        shutil.rmtree(media_dir.absolute().as_posix())
        shutil.move(
            dir.joinpath("pic").absolute().as_posix(), media_dir.absolute().as_posix()
        )
        code = process.returncode
        if code != 0:
            err = stderr.decode()
            raise Exception(f"parse doc failed: {err}")

        pure_text_path = dir.joinpath("text")

        with open(pure_text_path, "r") as f:
            content = f.read()

        pages = [
            Page(page_no=idx, content=x)
            for idx, x in enumerate(content.split("[pedia-page]"))
        ]

        for page in pages:
            content: str = page.pop("content")
            content_list = [
                Content(data=x.strip(), type="text")
                for x in content.split("\n")
                if x.strip()
            ]

            for content in content_list:
                if not content["data"].startswith("[pedia-"):
                    continue
                if content["data"] == "[pedia-badpic]" or content["data"].startswith("[pedia-pic"):
                    continue
                else:
                    content["data"] = content["data"] + "\n"

            page["content_list"] = content_list

        return pages

