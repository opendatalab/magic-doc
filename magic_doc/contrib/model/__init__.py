from abc import ABC, abstractmethod
from typing import List, TypeAlias, TypedDict
from werkzeug.datastructures import FileStorage


class Content(TypedDict):
    # 类型: image/text/md
    type: str

    # 数据
    # image: s3路径 s3://doc/xxx.png
    # text: 文本行
    # md: Markdown格式的文本
    data: str


class Page(TypedDict):
    # 从0开始
    page_no: int

    # 内容列表
    content_list: List[Content]


ExtractResponse: TypeAlias = List[Page]


if __name__ == "__main__":
    pages_data: ExtractResponse = [
        {
            "page_no": 0,
            "content_list": [
                {
                    "type": "text",
                    "data": "This is some text content.",
                },
                {
                    "type": "image",
                    "data": "s3://somebucket/imagepath.jpg",
                },
            ],
        }
    ]


class Extractor(ABC):
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def run(self, file_parse_id: str, r: FileStorage, skip_image: bool = True) -> ExtractResponse:
        pass
