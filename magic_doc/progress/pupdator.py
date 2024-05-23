
from abc import ABC, abstractmethod


class ConvProgressUpdator(object):
    def __init__(self):
        pass

    def update(self, progress: int) -> bool:
        # TODO ratelimie
        return self.do_update(progress)
    
    @abstractmethod
    def do_update(self, progress: int):
        pass
    

