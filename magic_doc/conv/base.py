
from abc import ABC, abstractmethod

class BaseConv(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def to_md(self, bits: bytes | str) -> str:
        return NotImplemented


