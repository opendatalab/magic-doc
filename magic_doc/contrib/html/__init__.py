from abc import ABC
from pathlib import Path
from werkzeug.datastructures import FileStorage

from magic_doc.contrib.model import ExtractResponse, Extractor


class HtmlExtractor(Extractor, ABC):
    def __init__(self) -> None:
        super().__init__()

    def setup(self):
        pass

    def run(id: str, r: FileStorage | Path, skip_image: bool = True) -> ExtractResponse:
        return []
