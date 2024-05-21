import requests
import json

from pathlib import Path


from werkzeug.datastructures import FileStorage

from pedia_document_parser.office import OfficeExtractor
from pedia_document_parser.model import ExtractResponse


class PptExtractor(OfficeExtractor):
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
            data = r.stream.read()
        elif issubclass(type(r), Path):
            with open(r, "rb") as data_file:
                data = data_file.read()

        files = {"file": data}
        response = requests.post(f"{self.config.tika}/api/v1/parse", files=files)
        self.upload_background(id, {})
        return response.json()["pages"]


if __name__ == "__main__":
    e = PptExtractor()
    print(
        json.dumps(
            e.run(
                "def",
                Path(
                    "/home/SENSETIME/wuziming/diclm/doc2docx/doc/【中繁-课件】物理学简介.ppt",
                ),
            ),
            ensure_ascii=False,
            indent=4,
        )
    )
    e.wait_all()
