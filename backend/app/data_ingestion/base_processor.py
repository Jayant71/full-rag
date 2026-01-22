from abc import ABC, abstractmethod


class Processor(ABC):
    @abstractmethod
    def process(self, file_path: str):
        pass
