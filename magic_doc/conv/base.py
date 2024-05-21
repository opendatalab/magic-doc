
from abc import ABC, abstractmethod

class Base(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def to_md(self, bits: bytes) -> str:
        return NotImplemented


