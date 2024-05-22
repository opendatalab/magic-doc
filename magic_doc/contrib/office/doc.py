import shutil
import json

from loguru import logger
from pathlib import Path
from subprocess import Popen

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
        process = Popen(cmd, shell=True, cwd=Path(cwd_path))
        process.wait()

        shutil.rmtree(media_dir.absolute().as_posix())
        shutil.move(
            dir.joinpath("pic").absolute().as_posix(), media_dir.absolute().as_posix()
        )
        code = process.returncode
        if code != 0:
            err = process.stderr.read().decode()
            raise Exception(f"parse doc failed: {err}")

        pure_text_path = dir.joinpath("text")

        with open(pure_text_path, "r") as f:
            content = f.read()

        # img_map: dict[Path, str] = {}
        # imgs = media_dir.glob("*")
        # for img in imgs:
        #     img_map[img] = self.generate_img_path(id, img.name)
        #
        # self.upload_background(id, img_map)

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
                if content["data"] == "[pedia-badpic]":
                    content["data"] = ""
                    content["type"] = "image"
                elif content["data"].startswith("[pedia-pic"):
                    content["type"] = "image"
                    img_name = content["data"][len("[pedia-") : -1]
                    img_path = media_dir.joinpath(img_name)
                    content["data"] = img_map[img_path]
                else:
                    content["data"] = content["data"] + "\n"

            page["content_list"] = content_list

        return pages


if __name__ == "__main__":
    e = DocExtractor()
    print(
        json.dumps(
            e.run("abc", Path("/home/SENSETIME/wuziming/diclm/doc2docx/doc/md4.doc")),
            ensure_ascii=False,
            indent=4,
        ),
    )
    e.wait_all()
