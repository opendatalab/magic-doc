import shutil

from abc import ABC, abstractmethod

from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Tuple

from loguru import logger
from werkzeug.datastructures import FileStorage

# from pedia_document_parser.config import Config
from magic_doc.contrib.model import ExtractResponse, Extractor
# from pedia_document_parser.s3.client import S3Client


class OfficeExtractor(Extractor, ABC):
    def __init__(self) -> None:
        super().__init__()
        # self.config = Config()
        self.tpe = ThreadPoolExecutor(max_workers=30)
        self.counter = {}
        self.tmp_dir = Path("/tmp")
        self.max_text_count = 50_0000

    # def generate_img_path(self, id: str, image_name: str) -> str:
    #     return f"s3://{self.config.s3_bucket}/{datetime.today().strftime('%Y-%m-%d')}/{id}/{image_name}"
    #
    # def upload(self, id: str, s3_path: str, path: Path) -> Tuple[str, str]:
    #     cli = S3Client(self.config.s3_ak, self.config.s3_sk, self.config.s3_ep)
    #     cli.upload_file(s3_path, path.absolute().as_posix())
    #     return (id, s3_path)

    # def upload_background(self, id: str, img_map: dict[Path, str]):
    #     if len(img_map) == 0:
    #         self.clean_up(id)
    #         return
    #
    #     self.counter[id] = len(img_map)
    #     for src, dest in img_map.items():
    #         fut = self.tpe.submit(self.upload, id, dest, src)
    #         fut.add_done_callback(self.on_upload_succ)

    def clean_up(self, id: str):
        dir = self.get_dir_by_id(id).absolute().as_posix()
        shutil.rmtree(dir)
        self.counter.pop(id, 0)
        logger.debug(f"del {dir}")

    def on_upload_succ(self, fut: Future[Tuple[str, str]]) -> None:
        id, s3_path = fut.result()
        logger.debug(f"upload {s3_path} succ")

        self.counter[id] -= 1
        if self.counter[id] == 0:
            self.clean_up(id)

    def wait_all(self):
        self.tpe.shutdown(wait=True)

    def get_dir_by_id(self, id: str) -> Path:
        return self.tmp_dir.joinpath(id)

    def run(self, id: str, r: FileStorage, skip_image: bool = True) -> ExtractResponse:
        dir = self.get_dir_by_id(id)

        dir.mkdir()
        media_dir = dir.joinpath("media")
        media_dir.mkdir()

        try:
            return self.extract(r, id, dir, media_dir, skip_image)
        except Exception as e:
            self.clean_up(id)
            raise e

    @abstractmethod
    def extract(
        self,
        r: FileStorage | Path,
        id: str,
        dir: Path,
        media_dir: Path,
        skip_image: bool,
    ) -> ExtractResponse:
        pass
