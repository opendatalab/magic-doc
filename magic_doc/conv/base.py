
from abc import ABC, abstractmethod

from magic_doc.progress.pupdator import ConvProgressUpdator

class BaseConv(ABC):
    def __init__(self, pupdator: ConvProgressUpdator):
        self.__progress_updator = pupdator

    @abstractmethod
    def to_md(self, bits: bytes | str) -> str:
        return NotImplemented


